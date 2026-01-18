"""LangGraph state schemas for workflow execution."""

from typing import Annotated, Literal, Optional

from pydantic import BaseModel, Field


def merge_lists(left: list, right: list) -> list:
    """Reducer function to merge lists in graph state."""
    return left + right


class AgentResult(BaseModel):
    """Result from a single agent execution."""

    agent_name: str = Field(description="Name of the agent that produced this result")
    status: Literal["success", "error", "partial"] = Field(description="Execution status")
    message: str = Field(description="Human-readable result message")
    data: Optional[dict] = Field(default=None, description="Structured result data")
    tool_calls: list[dict] = Field(default_factory=list, description="Tools invoked by agent")


class GraphState(BaseModel):
    """State schema for the LangGraph workflow.

    This state is passed through the graph and accumulated as agents execute.
    """

    # Input
    request_id: str = Field(description="Unique identifier for this request")
    user_message: str = Field(description="Original user message")
    context: dict = Field(default_factory=dict, description="Additional context")

    # Classification
    target_agents: list[str] = Field(
        default_factory=list, description="Agents selected by classifier"
    )

    # Execution - using Annotated for reducer
    agent_results: Annotated[list[AgentResult], merge_lists] = Field(
        default_factory=list, description="Results from agent executions"
    )

    # Error handling
    errors: Annotated[list[dict], merge_lists] = Field(
        default_factory=list, description="Errors encountered during execution"
    )

    # Metadata
    current_agent: Optional[str] = Field(
        default=None, description="Currently executing agent"
    )
    completed_agents: list[str] = Field(
        default_factory=list, description="Agents that have completed"
    )
