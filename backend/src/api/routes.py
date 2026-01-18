"""API route definitions for Nexus backend.

Endpoints:
- GET /health - Health check
- POST /chat - Synchronous chat processing
- POST /chat/stream - SSE streaming chat
- GET /chat/stream - SSE streaming via GET (for EventSource)
- POST /approve - Approve/reject pending actions
- GET /approvals - List pending approvals
- GET /agents - List available agents
- GET /data/* - Data endpoints for frontend views
"""

import logging
import uuid
from datetime import datetime
from typing import Optional

from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse, FileResponse

from src.api.streaming import (
    create_event_stream,
    get_pending_approval,
    get_all_pending_approvals,
    update_approval_status,
    delete_approval,
)
from src.graph.workflow import run_agents_parallel, graph
from src.graph.classifier import classify_request
from src.models.requests import (
    ChatRequest,
    ChatResponse,
    AgentResultResponse,
    ApprovalRequest,
    ApprovalResponse,
    ApprovalListResponse,
    ErrorResponse,
    PendingApproval,
)
from src.models.state import GraphState

logger = logging.getLogger(__name__)

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def process_chat(request: ChatRequest) -> ChatResponse:
    """Process a chat request and return agent responses.

    This endpoint handles synchronous requests where the full response
    is returned after all agents complete their work.

    Args:
        request: Chat request with user message

    Returns:
        ChatResponse with all agent results
    """
    request_id = request.request_id or str(uuid.uuid4())

    logger.info(f"Processing chat request {request_id}: {request.message[:50]}...")

    try:
        # Build enhanced message with conversation context if available
        conversation_history = request.conversation_history or []
        enhanced_message = request.message

        if conversation_history:
            context_parts = []
            for msg in conversation_history[-5:]:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                agent = msg.get("agent", "")
                if role == "user":
                    context_parts.append(f"User: {content}")
                elif role == "assistant":
                    agent_label = f"[{agent}]" if agent else "[Assistant]"
                    truncated = content[:500] + "..." if len(content) > 500 else content
                    context_parts.append(f"{agent_label}: {truncated}")
            if context_parts:
                history_context = "\n".join(context_parts)
                enhanced_message = f"[Previous conversation context:\n{history_context}]\n\nCurrent request: {request.message}"

        # Create initial state
        state = GraphState(
            request_id=request_id,
            user_message=enhanced_message,
            context={
                **(request.context or {}),
                "original_message": request.message,
                "has_conversation_history": len(conversation_history) > 0,
            },
        )

        # Run classification
        classification_result = await classify_request(state)
        target_agents = classification_result.get("target_agents", [])

        if not target_agents:
            return ChatResponse(
                request_id=request_id,
                message=request.message,
                agents_invoked=[],
                results=[],
            )

        # Update state with classification results
        state.target_agents = target_agents
        state.extracted_entities = classification_result.get("extracted_entities", {})
        state.inferred_action = classification_result.get("inferred_action", "")

        # Run agents in parallel
        execution_result = await run_agents_parallel(state)

        # Convert results
        results = [
            AgentResultResponse(
                agent_name=r.agent_name,
                status=r.status,
                message=r.message,
                data=r.data,
                tool_calls=r.tool_calls,
            )
            for r in execution_result.get("agent_results", [])
        ]

        return ChatResponse(
            request_id=request_id,
            message=request.message,
            agents_invoked=execution_result.get("completed_agents", []),
            results=results,
        )

    except Exception as e:
        logger.error(f"Chat processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/stream")
async def process_chat_stream(request: ChatRequest):
    """Process a chat request with Server-Sent Events streaming.

    This endpoint streams agent updates in real-time as they execute,
    providing immediate feedback to the user.

    Events streamed:
    - classification: Initial routing decision
    - routing: Agent assignment
    - agent_start: When an agent begins processing
    - agent_tool_call: Tool invocation updates
    - agent_complete: When an agent finishes
    - approval_required: When HITL approval needed
    - complete: Final aggregated response
    - error: If something goes wrong

    Args:
        request: Chat request with user message

    Returns:
        EventSourceResponse for SSE streaming
    """
    logger.info(f"Starting SSE stream for: {request.message[:50]}...")
    return create_event_stream(request, parallel=True)


@router.get("/chat/stream")
async def process_chat_stream_get(
    message: str = Query(..., description="User message to process"),
    request_id: Optional[str] = Query(None, description="Optional request ID"),
    event_name: Optional[str] = Query(None, description="Event context"),
):
    """Process a chat request via GET for EventSource compatibility.

    This endpoint allows using the browser's native EventSource API
    which only supports GET requests.

    Args:
        message: User message to process
        request_id: Optional request identifier
        event_name: Optional event context

    Returns:
        EventSourceResponse for SSE streaming
    """
    request = ChatRequest(
        message=message,
        request_id=request_id,
        event_name=event_name,
    )
    return create_event_stream(request, parallel=True)


# Approval endpoints

@router.post("/approve", response_model=ApprovalResponse)
async def process_approval(request: ApprovalRequest) -> ApprovalResponse:
    """Approve, reject, or edit a pending action.

    This endpoint handles Human-in-the-Loop (HITL) approvals for
    high-stakes actions like generating invoices or posting to social media.

    Args:
        request: Approval request with decision

    Returns:
        ApprovalResponse with result
    """
    logger.info(f"Processing approval {request.approval_id}: {request.action}")

    approval = await get_pending_approval(request.approval_id)

    if not approval:
        raise HTTPException(
            status_code=404,
            detail=f"Approval {request.approval_id} not found",
        )

    if approval.status != "pending":
        raise HTTPException(
            status_code=400,
            detail=f"Approval {request.approval_id} is already {approval.status}",
        )

    try:
        if request.action == "approve":
            # Execute the approved action
            execution_result = {
                "executed": True,
                "action_type": approval.action_type,
                "message": f"Action '{approval.action_type}' executed successfully",
            }

            await update_approval_status(
                request.approval_id,
                "executed",
                execution_result=execution_result,
            )

            return ApprovalResponse(
                approval_id=request.approval_id,
                status="executed",
                message="Action approved and executed",
                result=execution_result,
            )

        elif request.action == "reject":
            await update_approval_status(
                request.approval_id,
                "rejected",
                reason=request.reason,
            )

            return ApprovalResponse(
                approval_id=request.approval_id,
                status="rejected",
                message=f"Action rejected" + (f": {request.reason}" if request.reason else ""),
            )

        elif request.action == "edit":
            if not request.edits:
                raise HTTPException(
                    status_code=400,
                    detail="Edits required for 'edit' action",
                )

            execution_result = {
                "executed": True,
                "action_type": approval.action_type,
                "edits_applied": request.edits,
            }

            await update_approval_status(
                request.approval_id,
                "executed",
                edits=request.edits,
                execution_result=execution_result,
            )

            return ApprovalResponse(
                approval_id=request.approval_id,
                status="executed",
                message="Action edited and executed",
                result=execution_result,
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Approval processing error: {e}")
        await update_approval_status(request.approval_id, "failed")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/approvals", response_model=ApprovalListResponse)
async def list_approvals() -> ApprovalListResponse:
    """List all pending approvals.

    Returns:
        ApprovalListResponse with pending approvals
    """
    pending = await get_all_pending_approvals()
    # Convert ApprovalDocument to PendingApproval for response compatibility
    pending_approvals = [
        PendingApproval(
            approval_id=a.approval_id,
            request_id=a.request_id,
            agent_name=a.agent_name,
            action_type=a.action_type,
            action_description=a.action_description,
            action_data=a.action_data,
            created_at=a.created_at,
            expires_at=a.expires_at,
            status=a.status,
        )
        for a in pending
    ]
    return ApprovalListResponse(
        pending=pending_approvals,
        count=len(pending_approvals),
    )


@router.get("/approvals/{approval_id}")
async def get_approval(approval_id: str):
    """Get details of a specific approval.

    Args:
        approval_id: ID of the approval to retrieve

    Returns:
        Approval details
    """
    approval = await get_pending_approval(approval_id)
    if not approval:
        raise HTTPException(
            status_code=404,
            detail=f"Approval {approval_id} not found",
        )
    return approval


@router.delete("/approvals/{approval_id}")
async def cancel_approval(approval_id: str):
    """Cancel/delete a pending approval.

    Args:
        approval_id: ID of the approval to cancel

    Returns:
        Confirmation message
    """
    deleted = await delete_approval(approval_id)
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail=f"Approval {approval_id} not found",
        )

    return {"message": f"Approval {approval_id} cancelled"}


# Agent info endpoints

@router.get("/agents")
async def list_agents() -> dict:
    """List available agents and their capabilities."""
    return {
        "agents": [
            {
                "name": "partnerships",
                "description": "Handles sponsors, judges, mentors, and partner outreach",
                "tools": [
                    "search_partnership_sheet",
                    "draft_linkedin_outreach",
                    "draft_email_outreach",
                    "log_partnership_status",
                    "prepare_calendly_link",
                    "get_partnership_summary",
                ],
            },
            {
                "name": "marketing",
                "description": "Handles social media, content creation, and promotions",
                "tools": [
                    "create_content_timeline",
                    "draft_social_post",
                    "check_figma_asset",
                    "schedule_instagram_post",
                    "schedule_linkedin_post",
                    "get_campaign_ideas",
                    "update_sponsor_in_content",
                ],
            },
            {
                "name": "finance",
                "description": "Handles budgets, expenses, and financial tracking",
                "tools": [
                    "draft_mou",
                    "generate_invoice",
                    "update_budget_sheet",
                    "check_budget_status",
                    "get_sponsorship_financials",
                ],
            },
            {
                "name": "events",
                "description": "Handles event logistics, scheduling, and coordination",
                "tools": [
                    "send_availability_poll",
                    "update_logistics_sheet",
                    "get_logistics_summary",
                    "create_room_booking_request",
                    "generate_event_schedule",
                    "send_team_reminder",
                    "announce_to_slack",
                ],
            },
            {
                "name": "developers",
                "description": "Handles technical tasks, GitHub, and development workflows",
                "tools": [
                    "create_github_issue",
                    "check_pr_status",
                    "get_repo_updates",
                    "assign_issue",
                ],
            },
        ]
    }


@router.get("/health")
async def health_check() -> dict:
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "nexus-backend",
    }


@router.get("/health/agents")
async def check_agents_health() -> dict:
    """Check health status of all agents."""
    from src.graph.workflow import AGENT_RUNNERS

    return {
        "status": "healthy",
        "agents": {
            name: "registered" for name in AGENT_RUNNERS.keys()
        },
        "count": len(AGENT_RUNNERS),
    }


# Data endpoints for frontend views

@router.get("/data/partnerships")
async def get_partnerships_data() -> dict:
    """Get partnerships data for the Partnerships view.

    Fetches from Google Sheets (via MCP) with MongoDB as cache/fallback.
    """
    from src.tools.google_sheets import _get_sheet_data

    # Get sponsors from Google Sheets/MongoDB
    sponsors = []
    try:
        sponsor_data = await _get_sheet_data("Boothing Companies")
        for row in sponsor_data[1:]:  # Skip header
            if len(row) >= 5:
                sponsors.append({
                    "company": row[0] if len(row) > 0 else "",
                    "contact": row[1] if len(row) > 1 else "",
                    "email": row[2] if len(row) > 2 else "",
                    "position": row[3] if len(row) > 3 else "",
                    "status": row[4] if len(row) > 4 else "",
                    "tier": row[5] if len(row) > 5 else "",
                    "notes": row[6] if len(row) > 6 else "",
                })
    except Exception as e:
        logger.error(f"Failed to get sponsors: {e}")

    # Get judges
    judges = []
    try:
        judge_data = await _get_sheet_data("Judges")
        for row in judge_data[1:]:
            if len(row) >= 5:
                judges.append({
                    "company": row[0] if len(row) > 0 else "",
                    "contact": row[1] if len(row) > 1 else "",
                    "email": row[2] if len(row) > 2 else "",
                    "position": row[3] if len(row) > 3 else "",
                    "status": row[4] if len(row) > 4 else "",
                    "role": row[5] if len(row) > 5 else "",
                })
    except Exception as e:
        logger.error(f"Failed to get judges: {e}")

    # Get mentors
    mentors = []
    try:
        mentor_data = await _get_sheet_data("Mentors")
        for row in mentor_data[1:]:
            if len(row) >= 5:
                mentors.append({
                    "company": row[0] if len(row) > 0 else "",
                    "contact": row[1] if len(row) > 1 else "",
                    "email": row[2] if len(row) > 2 else "",
                    "position": row[3] if len(row) > 3 else "",
                    "status": row[4] if len(row) > 4 else "",
                    "role": row[5] if len(row) > 5 else "",
                })
    except Exception as e:
        logger.error(f"Failed to get mentors: {e}")

    return {
        "sponsors": sponsors,
        "judges": judges,
        "mentors": mentors,
        "summary": {
            "total_sponsors": len(sponsors),
            "confirmed": sum(1 for s in sponsors if s.get("status", "").lower() == "confirmed"),
            "pending": sum(1 for s in sponsors if s.get("status", "").lower() == "pending"),
            "in_discussion": sum(1 for s in sponsors if s.get("status", "").lower() == "in discussion"),
        },
    }


@router.get("/data/finance")
async def get_finance_data() -> dict:
    """Get finance data for the Finance view.

    Pulls sponsorship data from Google Sheets/MongoDB to calculate totals.
    """
    from src.tools.google_sheets import _get_sheet_data
    from src.services.database import db_service

    # Tier amounts
    tier_amounts = {
        "Platinum Sponsor": 25000,
        "Gold Sponsor": 15000,
        "Silver Sponsor": 5000,
        "Bronze Sponsor": 2500,
    }

    # Get sponsor data
    tier_counts = {"Platinum": 0, "Gold": 0, "Silver": 0, "Bronze": 0}
    confirmed_total = 0
    pending_total = 0

    try:
        sponsor_data = await _get_sheet_data("Boothing Companies")
        for row in sponsor_data[1:]:
            if len(row) >= 6:
                status = row[4] if len(row) > 4 else ""
                role = row[5] if len(row) > 5 else ""
                amount = tier_amounts.get(role, 0)

                # Count tiers
                for tier in tier_counts.keys():
                    if tier in role:
                        tier_counts[tier] += 1

                if status == "Confirmed":
                    confirmed_total += amount
                elif status in ["Pending", "In Discussion"]:
                    pending_total += amount
    except Exception as e:
        logger.error(f"Failed to get finance data: {e}")

    # Get budget from MongoDB or use defaults
    total_expenses = 43000
    budget = {
        "total_budget": 100000,
        "confirmed_sponsorship": confirmed_total,
        "pending_sponsorship": pending_total,
        "expenses": {
            "venue": 15000,
            "catering": 8000,
            "marketing": 5000,
            "swag": 3000,
            "prizes": 10000,
            "misc": 2000,
        },
        "remaining": confirmed_total - total_expenses,
    }

    try:
        collection = db_service.db["budget"]
        stored_budget = await collection.find_one({"event_name": "Blueprint"})
        if stored_budget:
            budget["expenses"] = stored_budget.get("expenses", budget["expenses"])
    except Exception as e:
        logger.error(f"Failed to get budget from MongoDB: {e}")

    return {
        "budget": budget,
        "tiers": {
            "Platinum": {"count": tier_counts["Platinum"], "amount": 25000, "total": tier_counts["Platinum"] * 25000},
            "Gold": {"count": tier_counts["Gold"], "amount": 15000, "total": tier_counts["Gold"] * 15000},
            "Silver": {"count": tier_counts["Silver"], "amount": 5000, "total": tier_counts["Silver"] * 5000},
        },
        "goal": 100000,
        "confirmed_total": confirmed_total,
        "pending_total": pending_total,
    }


@router.get("/data/events")
async def get_events_data() -> dict:
    """Get events/logistics data for the Events view."""
    return {
        "event_name": "Blueprint",
        "venue": {
            "location": "Tech Campus Building A",
            "capacity": 500,
            "status": "Confirmed",
            "setup_time": "Day before, 2pm-8pm",
        },
        "schedule": {
            "check_in": "8:00 AM",
            "opening": "9:00 AM",
            "workshops": "10:00 AM - 5:00 PM",
            "closing": "6:00 PM",
        },
        "catering": {
            "breakfast": {"time": "8:00 AM", "type": "light"},
            "lunch": {"time": "12:00 PM", "type": "boxed"},
            "snacks": {"time": "3:00 PM", "type": "standard"},
        },
        "equipment": {
            "projectors": {"count": 5, "status": "confirmed"},
            "microphones": {"count": 10, "status": "confirmed"},
            "extension_cords": {"count": 50, "status": "pending"},
        },
        "tasks": [
            {"task": "Finalize catering menu", "status": "pending", "due": "1 week"},
            {"task": "Confirm AV equipment", "status": "in_progress", "due": "3 days"},
            {"task": "Send volunteer schedule", "status": "pending", "due": "5 days"},
        ],
    }


@router.get("/data/marketing")
async def get_marketing_data() -> dict:
    """Get marketing data for the Marketing view."""
    return {
        "campaigns": [
            {
                "name": "Early Bird Registration",
                "status": "active",
                "platforms": ["instagram", "linkedin", "twitter"],
                "progress": 75,
            },
            {
                "name": "Speaker Announcements",
                "status": "scheduled",
                "platforms": ["linkedin", "twitter"],
                "progress": 40,
            },
            {
                "name": "Sponsor Spotlights",
                "status": "planned",
                "platforms": ["instagram", "linkedin"],
                "progress": 10,
            },
        ],
        "content_calendar": [
            {"date": "2024-01-20", "type": "social", "platform": "instagram", "status": "scheduled"},
            {"date": "2024-01-22", "type": "email", "platform": "mailchimp", "status": "draft"},
            {"date": "2024-01-25", "type": "social", "platform": "linkedin", "status": "planned"},
        ],
        "assets": {
            "ready": 12,
            "in_progress": 5,
            "pending": 3,
        },
    }


@router.get("/data/developers")
async def get_developers_data() -> dict:
    """Get developers data for the Developers view."""
    return {
        "repository": {
            "name": "jimmysamportfolio/nexus",
            "open_prs": 3,
            "open_issues": 5,
            "recent_commits": 12,
        },
        "open_prs": [
            {"number": 42, "title": "Add authentication system", "author": "dev1", "status": "Ready for review"},
            {"number": 41, "title": "Fix API rate limiting", "author": "dev2", "status": "Changes requested"},
            {"number": 40, "title": "Update documentation", "author": "dev3", "status": "Draft"},
        ],
        "open_issues": [
            {"number": 55, "title": "Login bug on mobile", "labels": ["bug", "high-priority"], "assignee": "dev1"},
            {"number": 54, "title": "Feature request: Dark mode", "labels": ["enhancement"], "assignee": "dev2"},
            {"number": 52, "title": "Improve error messages", "labels": ["enhancement", "good-first-issue"], "assignee": None},
        ],
        "recent_activity": [
            {"type": "commit", "message": "feat: Add user authentication", "time": "3 days ago"},
            {"type": "commit", "message": "fix: Resolve API rate limiting", "time": "2 days ago"},
            {"type": "commit", "message": "docs: Update README", "time": "1 day ago"},
            {"type": "commit", "message": "refactor: Clean up API routes", "time": "today"},
        ],
    }


# History endpoints

@router.get("/history/{request_id}")
async def get_request_history(request_id: str) -> dict:
    """Get the full history of a specific request.

    Args:
        request_id: The request ID to look up

    Returns:
        Full request history including messages and agent executions
    """
    from src.services.database import db_service
    from src.repositories.chat_history_repository import ChatHistoryRepository

    history_repo = ChatHistoryRepository(db_service.db)
    history = await history_repo.get_full_history(request_id)

    if not history.get("request"):
        raise HTTPException(
            status_code=404,
            detail=f"Request {request_id} not found",
        )

    return history


@router.get("/history")
async def list_recent_requests(
    limit: int = Query(default=50, le=100, description="Maximum number of requests"),
    status: Optional[str] = Query(default=None, description="Filter by status"),
) -> dict:
    """List recent requests.

    Args:
        limit: Maximum number of requests to return
        status: Optional status filter

    Returns:
        List of recent requests
    """
    from src.services.database import db_service
    from src.repositories.chat_history_repository import ChatHistoryRepository

    history_repo = ChatHistoryRepository(db_service.db)
    requests = await history_repo.requests.get_recent_requests(limit=limit, status=status)

    return {
        "requests": [r.model_dump() for r in requests],
        "count": len(requests),
    }


# File download endpoints

GENERATED_FILES_DIR = Path(__file__).parent.parent / "tools" / "generated"


@router.get("/files/{filename}")
async def download_file(filename: str):
    """Download a generated file.

    Args:
        filename: Name of the file to download

    Returns:
        FileResponse for the requested file
    """
    # Security: only allow files from the generated directory
    file_path = GENERATED_FILES_DIR / filename

    # Prevent directory traversal attacks
    try:
        file_path = file_path.resolve()
        if not str(file_path).startswith(str(GENERATED_FILES_DIR.resolve())):
            raise HTTPException(status_code=403, detail="Access denied")
    except Exception:
        raise HTTPException(status_code=403, detail="Invalid file path")

    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"File '{filename}' not found")

    # Determine media type based on extension
    media_type = "application/octet-stream"
    if filename.endswith(".docx"):
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    elif filename.endswith(".pdf"):
        media_type = "application/pdf"
    elif filename.endswith(".xlsx"):
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type=media_type,
    )


@router.get("/files")
async def list_generated_files() -> dict:
    """List all generated files available for download.

    Returns:
        List of generated files with metadata
    """
    files = []

    if GENERATED_FILES_DIR.exists():
        for file_path in GENERATED_FILES_DIR.iterdir():
            if file_path.is_file() and not file_path.name.startswith("."):
                stat = file_path.stat()
                files.append({
                    "filename": file_path.name,
                    "size": stat.st_size,
                    "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    "download_url": f"/api/files/{file_path.name}",
                })

    # Sort by creation time, newest first
    files.sort(key=lambda x: x["created_at"], reverse=True)

    return {
        "files": files,
        "count": len(files),
    }
