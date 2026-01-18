"""Router node for dispatching requests to specialized agents.

The router takes the classification output and creates agent assignments
with sub-prompts for parallel execution.
"""

import logging
from typing import Literal

from pydantic import BaseModel, Field

from src.models.state import GraphState

logger = logging.getLogger(__name__)

# Valid agent names
VALID_AGENTS = ["partnerships", "marketing", "finance", "events", "developers"]

# Type for routing decisions
AgentName = Literal["partnerships", "marketing", "finance", "events", "developers"]


class AgentAssignment(BaseModel):
    """Assignment of a task to a specific agent."""

    agent_name: AgentName = Field(description="Name of the assigned agent")
    sub_prompt: str = Field(description="Specific task for this agent")
    priority: int = Field(default=1, ge=1, le=5, description="Execution priority (1=highest)")


class RouterOutput(BaseModel):
    """Output from the router containing all agent assignments."""

    assignments: list[AgentAssignment] = Field(
        default_factory=list,
        description="List of agent assignments for parallel execution"
    )
    should_execute_parallel: bool = Field(
        default=True,
        description="Whether agents should run in parallel"
    )


def get_agent_sub_prompt(agent_name: str, user_message: str) -> str:
    """Generate a sub-prompt for a specific agent based on the user's message.

    Args:
        agent_name: The agent to generate a sub-prompt for
        user_message: The original user message

    Returns:
        A tailored sub-prompt for the agent
    """
    # For now, pass the full message to each agent
    # In the future, this could use LLM to decompose into specific tasks
    return user_message


def create_agent_assignments(
    target_agents: list[str],
    user_message: str,
) -> list[AgentAssignment]:
    """Create assignments for all target agents.

    Args:
        target_agents: List of agent names from classifier
        user_message: Original user message

    Returns:
        List of AgentAssignment objects
    """
    assignments = []

    for agent_name in target_agents:
        if agent_name not in VALID_AGENTS:
            logger.warning(f"Invalid agent name: {agent_name}")
            continue

        sub_prompt = get_agent_sub_prompt(agent_name, user_message)
        assignment = AgentAssignment(
            agent_name=agent_name,
            sub_prompt=sub_prompt,
            priority=1,  # All agents same priority for parallel execution
        )
        assignments.append(assignment)

    return assignments


def route_to_agents(
    state: GraphState,
) -> Literal["partnerships", "marketing", "finance", "events", "developers", "aggregate"]:
    """Route to appropriate agent node based on classification.

    This is a simple router that returns the first agent for sequential execution.
    For parallel execution, see `route_to_all_agents`.

    Args:
        state: Current graph state with target_agents populated

    Returns:
        Next node to execute
    """
    if not state.target_agents:
        logger.info("No target agents, skipping to aggregation")
        return "aggregate"

    # Return first valid agent
    for agent in state.target_agents:
        if agent in VALID_AGENTS:
            logger.info(f"Routing to agent: {agent}")
            return agent

    logger.warning("No valid agents found, skipping to aggregation")
    return "aggregate"


def get_all_target_agents(state: GraphState) -> list[str]:
    """Get all valid target agents from state.

    Args:
        state: Current graph state

    Returns:
        List of valid agent names
    """
    return [a for a in state.target_agents if a in VALID_AGENTS]


def should_run_agent(agent_name: str) -> callable:
    """Create a condition function for checking if an agent should run.

    Args:
        agent_name: The agent to check for

    Returns:
        Function that checks if the agent is in target_agents
    """
    def check(state: GraphState) -> bool:
        return agent_name in state.target_agents
    return check


async def router_node(state: GraphState) -> dict:
    """Router node that creates agent assignments for parallel execution.

    This node processes the classifier output and prepares assignments
    for each target agent.

    Args:
        state: Current graph state with target_agents populated

    Returns:
        Dict with router_output containing agent assignments
    """
    target_agents = state.target_agents
    user_message = state.user_message

    if not target_agents:
        logger.info("No target agents to route")
        return {"router_output": RouterOutput(assignments=[])}

    # Create assignments for all agents
    assignments = create_agent_assignments(target_agents, user_message)

    logger.info(f"Created {len(assignments)} agent assignments: {[a.agent_name for a in assignments]}")

    return {
        "router_output": RouterOutput(
            assignments=assignments,
            should_execute_parallel=len(assignments) > 1,
        )
    }


def get_parallel_agent_nodes(state: GraphState) -> list[str]:
    """Determine which agent nodes should execute in parallel.

    Args:
        state: Current graph state with target_agents

    Returns:
        List of agent node names to execute
    """
    valid_agents = [a for a in state.target_agents if a in VALID_AGENTS]

    if not valid_agents:
        return ["aggregate"]

    return valid_agents
