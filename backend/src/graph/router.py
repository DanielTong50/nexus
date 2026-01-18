"""Router logic for dispatching requests to agents.

Determines which agents should handle a request and creates
agent-specific sub-prompts.
"""

import logging
from typing import Literal

from pydantic import BaseModel, Field

from src.models.state import GraphState

logger = logging.getLogger(__name__)

# Valid agent names
VALID_AGENTS = {"partnerships", "marketing", "finance", "events", "developers"}


class AgentAssignment(BaseModel):
    """Assignment of a task to an agent."""

    agent_name: str = Field(description="Name of the agent")
    sub_prompt: str = Field(description="Agent-specific prompt")
    priority: int = Field(default=1, description="Execution priority")


class RouterOutput(BaseModel):
    """Output from the router node."""

    assignments: list[AgentAssignment] = Field(default_factory=list)
    should_execute_parallel: bool = Field(default=True)


def get_agent_sub_prompt(agent_name: str, user_message: str) -> str:
    """Generate an agent-specific sub-prompt.

    Args:
        agent_name: Name of the agent
        user_message: Original user message

    Returns:
        Sub-prompt tailored for the agent
    """
    # For now, return the full message
    # Backend Dev 2 can enhance this with LLM-based decomposition
    return user_message


def create_agent_assignments(
    target_agents: list[str],
    user_message: str,
) -> list[AgentAssignment]:
    """Create assignments for all target agents.

    Args:
        target_agents: List of agent names
        user_message: Original user message

    Returns:
        List of AgentAssignment objects
    """
    assignments = []

    for agent_name in target_agents:
        if agent_name not in VALID_AGENTS:
            logger.warning(f"Skipping invalid agent: {agent_name}")
            continue

        sub_prompt = get_agent_sub_prompt(agent_name, user_message)
        assignment = AgentAssignment(
            agent_name=agent_name,
            sub_prompt=sub_prompt,
            priority=1,
        )
        assignments.append(assignment)

    return assignments


def route_to_agents(
    state: GraphState,
) -> Literal["partnerships", "marketing", "finance", "events", "developers", "aggregate"]:
    """Route to the first valid agent (for sequential execution).

    Args:
        state: Current graph state

    Returns:
        Name of the next node to execute
    """
    target_agents = state.target_agents

    if not target_agents:
        return "aggregate"

    # Filter to valid agents
    valid_targets = [a for a in target_agents if a in VALID_AGENTS]

    if not valid_targets:
        return "aggregate"

    # Return first agent for sequential mode
    return valid_targets[0]


async def router_node(state: GraphState) -> dict:
    """Router node for the workflow graph.

    Creates agent assignments for parallel execution.

    Args:
        state: Current graph state

    Returns:
        Dict with router_output
    """
    assignments = create_agent_assignments(
        target_agents=state.target_agents,
        user_message=state.user_message,
    )

    output = RouterOutput(
        assignments=assignments,
        should_execute_parallel=len(assignments) > 1,
    )

    logger.info(f"Router created {len(assignments)} assignments, parallel={output.should_execute_parallel}")

    return {"router_output": output}


# Helper functions

def get_all_target_agents(state: GraphState) -> list[str]:
    """Get all valid target agents from state."""
    return [a for a in state.target_agents if a in VALID_AGENTS]


def get_parallel_agent_nodes(state: GraphState) -> list[str]:
    """Get agent nodes for parallel execution."""
    agents = get_all_target_agents(state)
    return agents if agents else ["aggregate"]


def should_run_agent(state: GraphState, agent_name: str) -> bool:
    """Check if a specific agent should run."""
    return agent_name in state.target_agents and agent_name in VALID_AGENTS
