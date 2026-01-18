"""LangGraph state schemas for workflow execution."""

from typing import Annotated, Any, Literal, Optional, TYPE_CHECKING

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from src.models.task_plan import TaskPlan


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
    pending_actions: list[dict] = Field(default_factory=list, description="Actions pending approval")


class GraphState(BaseModel):
    """State schema for the LangGraph workflow.

    This state is passed through the graph and accumulated as agents execute.
    """

    # Input
    request_id: str = Field(description="Unique identifier for this request")
    user_message: str = Field(description="Original user message")
    context: dict = Field(default_factory=dict, description="Additional context")
    
    # Organization context
    org_id: str = Field(default="default", description="Organization identifier")

    # Classification (legacy - for backward compatibility)
    target_agents: list[str] = Field(
        default_factory=list, description="Agents selected by classifier"
    )
    
    # Task Plan (new - for structured workflows)
    task_plan: Optional[Any] = Field(
        default=None, description="Structured task plan from enhanced classifier"
    )
    
    # Task execution tracking
    completed_task_ids: list[str] = Field(
        default_factory=list, description="IDs of completed tasks"
    )
    task_results: dict[str, Any] = Field(
        default_factory=dict, description="Results keyed by task ID"
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
    current_task_id: Optional[str] = Field(
        default=None, description="Currently executing task ID"
    )
    completed_agents: list[str] = Field(
        default_factory=list, description="Agents that have completed"
    )
    
    def has_task_plan(self) -> bool:
        """Check if this state has a structured task plan."""
        return self.task_plan is not None
    
    def get_completed_task_ids(self) -> set[str]:
        """Get set of completed task IDs for dependency checking."""
        return set(self.completed_task_ids)
