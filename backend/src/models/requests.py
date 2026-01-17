"""API request and response models."""

from typing import Literal, Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request model for chat endpoints."""

    message: str = Field(description="User message to process")
    request_id: Optional[str] = Field(default=None, description="Optional request identifier")
    context: dict = Field(default_factory=dict, description="Additional context for agents")


class AgentResultResponse(BaseModel):
    """Response model for individual agent results."""

    agent_name: str
    status: Literal["success", "error", "partial"]
    message: str
    data: Optional[dict] = None


class ChatResponse(BaseModel):
    """Response model for synchronous chat endpoint."""

    request_id: str
    message: str
    agents_invoked: list[str]
    results: list[AgentResultResponse]


class StreamEvent(BaseModel):
    """Model for SSE stream events."""

    event_type: Literal[
        "classification",
        "agent_start",
        "agent_update",
        "agent_complete",
        "complete",
        "error",
    ]
    data: dict


class ErrorResponse(BaseModel):
    """Standard error response model."""

    error: str
    detail: Optional[str] = None
    request_id: Optional[str] = None
