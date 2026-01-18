"""LangGraph workflow definition for multi-agent orchestration.

This module defines the workflow graph that:
1. Classifies user requests
2. Routes to appropriate agents
3. Executes agents in parallel using asyncio.gather
4. Aggregates results

Dual-Engine LLM Strategy:
- Classifier: Always Gemini 1.5 Pro
- Agents: Configurable via ACTIVE_AGENT_PROVIDER (Gemini Flash or Vultr/Llama)
"""

import asyncio
import logging
import time
from typing import Any, Literal, Optional

from langgraph.graph import END, StateGraph

from config.settings import settings
from src.models.state import AgentResult, GraphState

logger = logging.getLogger(__name__)

# Valid agent names
VALID_AGENTS = {"partnerships", "marketing", "finance", "events", "developers"}

# Agent runner registry
AGENT_RUNNERS: dict[str, Any] = {}


def register_agent(name: str):
    """Decorator to register an agent runner function."""

    def decorator(func):
        AGENT_RUNNERS[name] = func
        return func

    return decorator


# =============================================================================
# Placeholder Agent Runners (Backend Dev 2 will implement actual agents)
# =============================================================================


@register_agent("partnerships")
async def run_partnerships_agent(state: GraphState) -> dict:
    """Execute the partnerships agent."""
    start_time = time.time()
    await asyncio.sleep(0.01)  # Simulate work

    result = AgentResult(
        agent_name="partnerships",
        status="success",
        message="Partnerships agent executed",
        data={"execution_time": time.time() - start_time},
    )
    logger.info(f"Partnerships agent completed in {time.time() - start_time:.3f}s")
    return {"agent_results": [result], "completed_agents": ["partnerships"]}


@register_agent("marketing")
async def run_marketing_agent(state: GraphState) -> dict:
    """Execute the marketing agent."""
    start_time = time.time()
    await asyncio.sleep(0.01)

    result = AgentResult(
        agent_name="marketing",
        status="success",
        message="Marketing agent executed",
        data={"execution_time": time.time() - start_time},
    )
    logger.info(f"Marketing agent completed in {time.time() - start_time:.3f}s")
    return {"agent_results": [result], "completed_agents": ["marketing"]}


@register_agent("finance")
async def run_finance_agent(state: GraphState) -> dict:
    """Execute the finance agent."""
    start_time = time.time()
    await asyncio.sleep(0.01)

    result = AgentResult(
        agent_name="finance",
        status="success",
        message="Finance agent executed",
        data={"execution_time": time.time() - start_time},
    )
    logger.info(f"Finance agent completed in {time.time() - start_time:.3f}s")
    return {"agent_results": [result], "completed_agents": ["finance"]}


@register_agent("events")
async def run_events_agent(state: GraphState) -> dict:
    """Execute the events agent."""
    start_time = time.time()
    await asyncio.sleep(0.01)

    result = AgentResult(
        agent_name="events",
        status="success",
        message="Events agent executed",
        data={"execution_time": time.time() - start_time},
    )
    logger.info(f"Events agent completed in {time.time() - start_time:.3f}s")
    return {"agent_results": [result], "completed_agents": ["events"]}


@register_agent("developers")
async def run_developers_agent(state: GraphState) -> dict:
    """Execute the developers agent."""
    start_time = time.time()
    await asyncio.sleep(0.01)

    result = AgentResult(
        agent_name="developers",
        status="success",
        message="Developers agent executed",
        data={"execution_time": time.time() - start_time},
    )
    logger.info(f"Developers agent completed in {time.time() - start_time:.3f}s")
    return {"agent_results": [result], "completed_agents": ["developers"]}


# =============================================================================
# Parallel Agent Execution
# =============================================================================


async def run_agents_parallel(state: GraphState) -> dict:
    """Execute all target agents in parallel using asyncio.gather.

    Args:
        state: Current graph state with target_agents populated

    Returns:
        Dict with aggregated agent_results and completed_agents
    """
    target_agents = [a for a in state.target_agents if a in VALID_AGENTS]

    if not target_agents:
        logger.info("No target agents to execute")
        return {"agent_results": [], "completed_agents": []}

    logger.info(f"Executing {len(target_agents)} agents in parallel: {target_agents}")
    start_time = time.time()

    # Create tasks
    tasks = []
    for agent_name in target_agents:
        if agent_name in AGENT_RUNNERS:
            tasks.append(AGENT_RUNNERS[agent_name](state))
        else:
            logger.warning(f"No runner for agent: {agent_name}")

    # Execute in parallel
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Merge results
    all_results = []
    all_completed = []
    errors = []

    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logger.error(f"Agent {target_agents[i]} failed: {result}")
            errors.append({"agent": target_agents[i], "error": str(result)})
            all_results.append(
                AgentResult(
                    agent_name=target_agents[i],
                    status="error",
                    message=str(result),
                )
            )
        else:
            all_results.extend(result.get("agent_results", []))
            all_completed.extend(result.get("completed_agents", []))

    total_time = time.time() - start_time
    logger.info(f"Parallel execution completed in {total_time:.3f}s")

    output = {"agent_results": all_results, "completed_agents": all_completed}
    if errors:
        output["errors"] = errors

    return output


# =============================================================================
# Workflow Nodes
# =============================================================================


async def classify_node(state: GraphState) -> dict:
    """Classifier node - routes to the classifier."""
    from src.graph.classifier import classify_request

    return await classify_request(state)


def should_run_parallel(state: GraphState) -> Literal["parallel_agents", "aggregate"]:
    """Determine if we should run agents or skip to aggregation."""
    if state.target_agents:
        return "parallel_agents"
    return "aggregate"


async def aggregate_results(state: GraphState) -> dict:
    """Aggregate results from all executed agents."""
    logger.info(f"Aggregation: {len(state.agent_results)} results from {len(state.completed_agents)} agents")
    return {}


async def handle_error(state: GraphState) -> dict:
    """Handle errors that occurred during execution."""
    logger.error(f"Error handler invoked with {len(state.errors)} errors")
    return {"errors": state.errors}


# =============================================================================
# Graph Definition
# =============================================================================


def create_workflow() -> StateGraph:
    """Create and compile the LangGraph workflow.

    Returns:
        Compiled StateGraph ready for execution.
    """
    workflow = StateGraph(GraphState)

    # Add nodes
    workflow.add_node("classify", classify_node)
    workflow.add_node("parallel_agents", run_agents_parallel)
    workflow.add_node("error_handler", handle_error)
    workflow.add_node("aggregate", aggregate_results)

    # Set entry point
    workflow.set_entry_point("classify")

    # Route from classifier
    workflow.add_conditional_edges(
        "classify",
        should_run_parallel,
        {
            "parallel_agents": "parallel_agents",
            "aggregate": "aggregate",
        },
    )

    # After parallel execution, go to aggregation
    workflow.add_edge("parallel_agents", "aggregate")

    # Error handler goes to end
    workflow.add_edge("error_handler", END)

    # Aggregation is the final step
    workflow.add_edge("aggregate", END)

    return workflow.compile()


# Create compiled workflow instance
graph = create_workflow()


# =============================================================================
# Convenience Functions
# =============================================================================


async def run_workflow(
    user_message: str,
    request_id: str = "default",
    event_id: Optional[str] = None,
) -> dict:
    """Run the workflow with a user message.

    Args:
        user_message: The user's input message
        request_id: Unique identifier for this request
        event_id: Optional event context

    Returns:
        Dict with workflow results
    """
    initial_state = GraphState(
        request_id=request_id,
        user_message=user_message,
        event_id=event_id,
    )

    result = await graph.ainvoke(initial_state)
    return result
