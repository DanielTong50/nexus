"""Chat history and request logging models for persistent storage."""

from datetime import datetime
from typing import Literal, Optional

from pydantic import Field

from src.models.base import BaseDocument


class RequestSummary(BaseDocument):
    """MongoDB document for tracking chat request lifecycle."""

    request_id: str = Field(description="Unique identifier for the request")
    user_id: Optional[str] = Field(default=None, description="User who made the request")
    user_message: str = Field(description="Original user message")
    event_name: Optional[str] = Field(default=None, description="Event context (e.g., 'Blueprint')")
    context: dict = Field(default_factory=dict, description="Additional context")
    target_agents: list[str] = Field(default_factory=list, description="Agents selected for this request")
    status: Literal["pending", "classifying", "executing", "completed", "error"] = Field(
        default="pending", description="Current request status"
    )
    classification_result: Optional[dict] = Field(
        default=None, description="Classification output"
    )
    completed_agents: list[str] = Field(
        default_factory=list, description="Agents that completed execution"
    )
    error_message: Optional[str] = Field(default=None, description="Error message if failed")
    started_at: datetime = Field(default_factory=datetime.utcnow, description="When processing started")
    completed_at: Optional[datetime] = Field(default=None, description="When processing completed")
    duration_ms: Optional[int] = Field(default=None, description="Total processing time in milliseconds")
    pending_approvals: list[str] = Field(
        default_factory=list, description="IDs of pending approvals from this request"
    )

    def complete(self, error: Optional[str] = None) -> None:
        """Mark the request as completed."""
        self.completed_at = datetime.utcnow()
        if self.started_at:
            self.duration_ms = int((self.completed_at - self.started_at).total_seconds() * 1000)
        self.status = "error" if error else "completed"
        if error:
            self.error_message = error


class ChatMessage(BaseDocument):
    """MongoDB document for individual chat messages."""

    request_id: str = Field(description="Reference to the parent request")
    role: Literal["user", "assistant", "system", "agent"] = Field(
        description="Message role"
    )
    content: str = Field(description="Message content")
    agent_name: Optional[str] = Field(
        default=None, description="Agent name if role is 'agent'"
    )
    metadata: dict = Field(default_factory=dict, description="Additional message metadata")


class AgentExecutionLog(BaseDocument):
    """MongoDB document for tracking individual agent executions."""

    request_id: str = Field(description="Reference to the parent request")
    agent_name: str = Field(description="Name of the agent")
    status: Literal["started", "executing", "completed", "error"] = Field(
        default="started", description="Execution status"
    )
    message: Optional[str] = Field(default=None, description="Agent response message")
    data: Optional[dict] = Field(default=None, description="Agent output data")
    tool_calls: list[dict] = Field(default_factory=list, description="Tools invoked by agent")
    pending_actions: list[dict] = Field(
        default_factory=list, description="Actions requiring approval"
    )
    error_message: Optional[str] = Field(default=None, description="Error if execution failed")
    started_at: datetime = Field(default_factory=datetime.utcnow, description="When agent started")
    completed_at: Optional[datetime] = Field(default=None, description="When agent completed")
    duration_ms: Optional[int] = Field(default=None, description="Execution time in milliseconds")

    def complete(self, status: Literal["completed", "error"], error: Optional[str] = None) -> None:
        """Mark the agent execution as completed."""
        self.completed_at = datetime.utcnow()
        if self.started_at:
            self.duration_ms = int((self.completed_at - self.started_at).total_seconds() * 1000)
        self.status = status
        if error:
            self.error_message = error


class ConversationThread(BaseDocument):
    """MongoDB document for grouping related requests into a conversation."""

    thread_id: str = Field(description="Unique thread identifier")
    user_id: Optional[str] = Field(default=None, description="User who owns this thread")
    title: Optional[str] = Field(default=None, description="Optional thread title")
    request_ids: list[str] = Field(default_factory=list, description="Requests in this thread")
    last_activity: datetime = Field(
        default_factory=datetime.utcnow, description="Last activity timestamp"
    )
    is_active: bool = Field(default=True, description="Whether thread is active")
