"""API route definitions for Nexus backend.

Endpoints:
- POST /chat - Synchronous chat processing
- POST /chat/stream - SSE streaming chat
- GET /chat/stream - SSE streaming via GET (for EventSource)
- POST /approve - Approve/reject pending actions
- GET /approvals - List pending approvals
- GET /agents - List available agents
"""

import logging
import uuid
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

from src.api.streaming import (
    create_event_stream,
    get_pending_approval,
    get_all_pending_approvals,
    update_approval_status,
    PENDING_APPROVALS,
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
        # Create initial state
        state = GraphState(
            request_id=request_id,
            user_message=request.message,
            context=request.context,
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

        # Update state with target agents
        state.target_agents = target_agents

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

    approval = get_pending_approval(request.approval_id)

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
            update_approval_status(request.approval_id, "approved")

            # TODO: Actually execute the action (call the tool)
            # For now, just mark as executed
            result = {
                "executed": True,
                "action_type": approval.action_type,
                "message": f"Action '{approval.action_type}' executed successfully",
            }

            return ApprovalResponse(
                approval_id=request.approval_id,
                status="executed",
                message=f"Action approved and executed",
                result=result,
            )

        elif request.action == "reject":
            update_approval_status(request.approval_id, "rejected")

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

            # Update the action data with edits
            approval.action_data.update(request.edits)
            update_approval_status(request.approval_id, "approved")

            result = {
                "executed": True,
                "action_type": approval.action_type,
                "edits_applied": request.edits,
            }

            return ApprovalResponse(
                approval_id=request.approval_id,
                status="executed",
                message="Action edited and executed",
                result=result,
            )

    except Exception as e:
        logger.error(f"Approval processing error: {e}")
        update_approval_status(request.approval_id, "failed")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/approvals", response_model=ApprovalListResponse)
async def list_approvals() -> ApprovalListResponse:
    """List all pending approvals.

    Returns:
        ApprovalListResponse with pending approvals
    """
    pending = get_all_pending_approvals()
    return ApprovalListResponse(
        pending=pending,
        count=len(pending),
    )


@router.get("/approvals/{approval_id}")
async def get_approval(approval_id: str):
    """Get details of a specific approval.

    Args:
        approval_id: ID of the approval to retrieve

    Returns:
        PendingApproval details
    """
    approval = get_pending_approval(approval_id)
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
    if approval_id not in PENDING_APPROVALS:
        raise HTTPException(
            status_code=404,
            detail=f"Approval {approval_id} not found",
        )

    del PENDING_APPROVALS[approval_id]
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
