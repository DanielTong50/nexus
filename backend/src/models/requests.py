"""API request and response models."""

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request model for chat endpoints."""

    message: str = Field(description="User message to process")
    request_id: Optional[str] = Field(default=None, description="Optional request identifier")
    event_name: Optional[str] = Field(default=None, description="Event context (e.g., 'Blueprint')")
    context: dict = Field(default_factory=dict, description="Additional context for agents")


class AgentResultResponse(BaseModel):
    """Response model for individual agent results."""

    agent_name: str
    status: Literal["success", "error", "partial"]
    message: str
    data: Optional[dict] = None
    tool_calls: list[dict] = Field(default_factory=list)
    document_links: list[dict] = Field(default_factory=list, description="Links to external docs")


class ChatResponse(BaseModel):
    """Response model for synchronous chat endpoint."""

    request_id: str
    message: str
    agents_invoked: list[str]
    results: list[AgentResultResponse]
    pending_approvals: list[str] = Field(default_factory=list, description="IDs of pending HITL actions")


class StreamEvent(BaseModel):
    """Model for SSE stream events."""

    event_type: Literal[
        "classification",
        "routing",
        "agent_start",
        "agent_update",
        "agent_tool_call",
        "agent_complete",
        "agent_error",
        "approval_required",
        "complete",
        "error",
    ]
    data: dict
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    agent_name: Optional[str] = None


class ErrorResponse(BaseModel):
    """Standard error response model."""

    error: str
    detail: Optional[str] = None
    request_id: Optional[str] = None


# Approval-related models

class PendingApproval(BaseModel):
    """Model for actions requiring user approval (HITL)."""

    approval_id: str = Field(description="Unique ID for this approval request")
    request_id: str = Field(description="Original request ID")
    agent_name: str = Field(description="Agent requesting approval")
    action_type: str = Field(description="Type of action (e.g., 'draft_mou', 'generate_invoice')")
    action_description: str = Field(description="Human-readable description")
    action_data: dict = Field(description="Data for the action")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = Field(default=None, description="When approval expires")
    status: Literal["pending", "approved", "rejected", "expired"] = Field(default="pending")


class ApprovalRequest(BaseModel):
    """Request to approve or reject a pending action."""

    approval_id: str = Field(description="ID of the approval to respond to")
    action: Literal["approve", "reject", "edit"] = Field(description="User's decision")
    edits: Optional[dict] = Field(default=None, description="Edits if action is 'edit'")
    reason: Optional[str] = Field(default=None, description="Optional reason for rejection")


class ApprovalResponse(BaseModel):
    """Response after processing an approval."""

    approval_id: str
    status: Literal["approved", "rejected", "executed", "failed"]
    message: str
    result: Optional[dict] = None


class ApprovalListResponse(BaseModel):
    """Response containing list of pending approvals."""

    pending: list[PendingApproval]
    count: int
