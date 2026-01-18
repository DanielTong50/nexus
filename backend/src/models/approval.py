"""Approval workflow models for HITL (Human-In-The-Loop) actions."""

from datetime import datetime, timedelta
from typing import Literal, Optional

from pydantic import BaseModel, Field

from src.models.base import BaseDocument


class ApprovalDocument(BaseDocument):
    """MongoDB document for pending approval requests."""

    approval_id: str = Field(description="Unique identifier for this approval")
    request_id: str = Field(description="Original chat request ID")
    agent_name: str = Field(description="Agent that requested approval")
    action_type: str = Field(description="Type of action requiring approval (e.g., 'draft_mou')")
    action_description: str = Field(description="Human-readable description of the action")
    action_data: dict = Field(default_factory=dict, description="Data for executing the action")
    status: Literal["pending", "approved", "rejected", "expired", "executed", "failed"] = Field(
        default="pending", description="Current approval status"
    )
    expires_at: Optional[datetime] = Field(
        default=None, description="When this approval expires"
    )
    approved_by: Optional[str] = Field(default=None, description="User who approved/rejected")
    approved_at: Optional[datetime] = Field(default=None, description="When approved/rejected")
    execution_result: Optional[dict] = Field(
        default=None, description="Result after action execution"
    )
    edits: Optional[dict] = Field(
        default=None, description="User edits if action was 'edit'"
    )
    rejection_reason: Optional[str] = Field(
        default=None, description="Reason if rejected"
    )

    @classmethod
    def create_with_expiry(
        cls,
        approval_id: str,
        request_id: str,
        agent_name: str,
        action_type: str,
        action_description: str,
        action_data: dict,
        expiry_hours: int = 24,
    ) -> "ApprovalDocument":
        """Create an approval document with automatic expiry."""
        return cls(
            approval_id=approval_id,
            request_id=request_id,
            agent_name=agent_name,
            action_type=action_type,
            action_description=action_description,
            action_data=action_data,
            expires_at=datetime.utcnow() + timedelta(hours=expiry_hours),
        )


class ApprovalHistoryEntry(BaseDocument):
    """Audit log entry for approval status changes."""

    approval_id: str = Field(description="Reference to the approval document")
    previous_status: Optional[str] = Field(
        default=None, description="Status before this change"
    )
    new_status: str = Field(description="Status after this change")
    changed_by: Optional[str] = Field(
        default=None, description="User or system that made the change"
    )
    reason: Optional[str] = Field(
        default=None, description="Reason for the status change"
    )
    metadata: dict = Field(
        default_factory=dict, description="Additional metadata about the change"
    )


class ApprovalStats(BaseModel):
    """Statistics about approvals."""

    total_pending: int = Field(default=0)
    total_approved: int = Field(default=0)
    total_rejected: int = Field(default=0)
    total_expired: int = Field(default=0)
    total_executed: int = Field(default=0)
    total_failed: int = Field(default=0)
    avg_approval_time_seconds: Optional[float] = Field(default=None)
