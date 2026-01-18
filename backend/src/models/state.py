"""LangGraph state definitions.

Defines the graph state that flows through the workflow.
"""

from typing import Annotated, Any, Literal, Optional

from langchain_core.messages import BaseMessage
from pydantic import BaseModel, Field


def add_messages(left: list[BaseMessage], right: list[BaseMessage]) -> list[BaseMessage]:
    """Reducer that appends messages."""
    return left + right


def add_errors(left: list[str], right: list[str]) -> list[str]:
    """Reducer that appends errors."""
    return left + right


class AgentResult(BaseModel):
    """Result from an agent execution."""

    agent_name: str = Field(description="Name of the agent")
    status: Literal["success", "error", "pending_approval"] = Field(default="success")
    message: str = Field(default="", description="Result message")
    data: Optional[dict[str, Any]] = Field(default=None, description="Result data")
    tool_calls: list[dict] = Field(default_factory=list, description="Tools invoked")
    requires_approval: bool = Field(default=False, description="Needs HITL approval")


class GraphState(BaseModel):
    """State that flows through the LangGraph workflow.

    Attributes:
        request_id: Unique identifier for this request
        user_message: Original user input
        event_id: Optional event context (e.g., "blueprint-2025")
        messages: Conversation history
        next_step: Current routing decision
        target_agents: Agents to invoke
        agent_results: Results from agent executions
        completed_agents: Agents that have finished
        errors: Error messages collected during execution
        context: Additional context for agents
    """

    # Request info
    request_id: str = Field(default="", description="Unique request identifier")
    user_message: str = Field(default="", description="Original user message")
    event_id: Optional[str] = Field(default=None, description="Event context")

    # Conversation state
    messages: Annotated[list[BaseMessage], add_messages] = Field(default_factory=list)

    # Routing state
    next_step: str = Field(default="classify", description="Next node to execute")
    target_agents: list[str] = Field(default_factory=list, description="Agents to invoke")

    # Execution results
    agent_results: list[AgentResult] = Field(default_factory=list)
    completed_agents: list[str] = Field(default_factory=list)

    # Error tracking
    errors: Annotated[list[str], add_errors] = Field(default_factory=list)

    # Context
    context: dict[str, Any] = Field(default_factory=dict, description="Additional context")

    class Config:
        arbitrary_types_allowed = True
