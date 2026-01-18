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

from src.api.streaming import create_event_stream
from src.graph.workflow import run_workflow
from src.models.requests import (
    ApprovalListResponse,
    ApprovalRequest,
    ApprovalResponse,
    ChatRequest,
    ChatResponse,
    AgentResultResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["chat"])


# =============================================================================
# Chat Endpoints
# =============================================================================


@router.post("/chat", response_model=ChatResponse)
async def process_chat(request: ChatRequest) -> ChatResponse:
    """Process a chat request and return agent responses.

    This endpoint handles synchronous requests where the full response
    is returned after all agents complete their work.
    """
    request_id = request.request_id or str(uuid.uuid4())

    logger.info(f"Processing chat request {request_id}: {request.message[:50]}...")

    try:
        result = await run_workflow(
            user_message=request.message,
            request_id=request_id,
            event_id=request.event_id,
        )

        # Convert results
        results = [
            AgentResultResponse(
                agent_name=r.agent_name,
                status=r.status,
                message=r.message,
                data=r.data,
                tool_calls=r.tool_calls,
                requires_approval=r.requires_approval,
            )
            for r in result.get("agent_results", [])
        ]

        return ChatResponse(
            request_id=request_id,
            message=request.message,
            agents_invoked=result.get("completed_agents", []),
            results=results,
        )

    except Exception as e:
        logger.error(f"Chat processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/stream")
async def process_chat_stream(request: ChatRequest):
    """Process a chat request with Server-Sent Events streaming.

    Streams agent updates in real-time as they execute.
    """
    logger.info(f"Starting SSE stream for: {request.message[:50]}...")
    return create_event_stream(request)


@router.get("/chat/stream")
async def process_chat_stream_get(
    message: str = Query(..., description="User message to process"),
    request_id: Optional[str] = Query(None, description="Optional request ID"),
    event_id: Optional[str] = Query(None, description="Event context"),
):
    """Process a chat request via GET for EventSource compatibility."""
    request = ChatRequest(
        message=message,
        request_id=request_id,
        event_id=event_id,
    )
    return create_event_stream(request)


# =============================================================================
# Approval Endpoints (HITL)
# =============================================================================

# In-memory store (replace with Redis/MongoDB in production)
_pending_approvals: dict[str, dict] = {}


@router.post("/approve", response_model=ApprovalResponse)
async def process_approval(request: ApprovalRequest) -> ApprovalResponse:
    """Approve, reject, or edit a pending action."""
    if request.approval_id not in _pending_approvals:
        raise HTTPException(status_code=404, detail="Approval not found")

    approval = _pending_approvals[request.approval_id]

    if approval.get("status") != "pending":
        raise HTTPException(status_code=400, detail="Approval already processed")

    if request.action == "approve":
        approval["status"] = "approved"
        return ApprovalResponse(
            approval_id=request.approval_id,
            status="executed",
            message="Action approved and executed",
        )
    elif request.action == "reject":
        approval["status"] = "rejected"
        return ApprovalResponse(
            approval_id=request.approval_id,
            status="rejected",
            message=f"Action rejected: {request.reason or 'No reason provided'}",
        )
    else:
        approval["data"].update(request.edits or {})
        approval["status"] = "approved"
        return ApprovalResponse(
            approval_id=request.approval_id,
            status="executed",
            message="Action edited and executed",
            result={"edits_applied": request.edits},
        )


@router.get("/approvals", response_model=ApprovalListResponse)
async def list_approvals() -> ApprovalListResponse:
    """List all pending approvals."""
    from src.models.requests import PendingApproval

    pending = [
        PendingApproval(**a) for a in _pending_approvals.values() if a.get("status") == "pending"
    ]
    return ApprovalListResponse(pending=pending, count=len(pending))


# =============================================================================
# Agent Info Endpoints
# =============================================================================


@router.get("/agents")
async def list_agents() -> dict:
    """List available agents and their capabilities."""
    from config.settings import settings

    return {
        "active_provider": settings.active_agent_provider,
        "agents": [
            {
                "name": "partnerships",
                "description": "Handles sponsors, judges, mentors, and partner outreach",
            },
            {
                "name": "marketing",
                "description": "Handles social media, content creation, and promotions",
            },
            {
                "name": "finance",
                "description": "Handles budgets, expenses, and financial tracking",
            },
            {
                "name": "events",
                "description": "Handles event logistics, scheduling, and coordination",
            },
            {
                "name": "developers",
                "description": "Handles technical tasks, GitHub, and development workflows",
            },
        ],
    }


@router.get("/config")
async def get_config() -> dict:
    """Get current configuration (non-sensitive)."""
    from config.settings import settings

    return {
        "environment": settings.environment,
        "active_agent_provider": settings.active_agent_provider,
        "classifier_model": settings.classifier_model,
        "agent_model": settings.agent_model,
    }
