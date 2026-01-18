"""LangGraph workflow definition for multi-agent orchestration.

This module defines the workflow graph that:
1. Classifies user requests
2. Routes to appropriate agents
3. Executes agents in parallel using asyncio.gather
4. Aggregates results

Agents use LLM to intelligently select and execute tools.
"""

import asyncio
import logging
import time
from typing import Literal

from langgraph.graph import END, StateGraph

from src.graph.classifier import classify_request
from src.graph.router import route_to_agents, VALID_AGENTS
from src.models.state import AgentResult, GraphState

logger = logging.getLogger(__name__)

# Agent runner registry - maps agent names to their execution functions
AGENT_RUNNERS = {}


def register_agent(name: str):
    """Decorator to register an agent runner function."""
    def decorator(func):
        AGENT_RUNNERS[name] = func
        return func
    return decorator


@register_agent("partnerships")
async def run_partnerships_agent(state: GraphState) -> dict:
    """Execute the partnerships agent with real LLM."""
    from src.agents.partnerships import partnerships_agent

    start_time = time.time()
    logger.info("Partnerships agent starting...")

    try:
        result = await partnerships_agent.execute(
            prompt=state.user_message,
            context={"event_id": state.event_id} if hasattr(state, 'event_id') else {}
        )

        agent_result = AgentResult(
            agent_name="partnerships",
            status="success" if result.success else "error",
            message=result.message,
            data={"execution_time": time.time() - start_time},
            tool_calls=result.tool_calls,
            pending_actions=result.pending_actions if hasattr(result, 'pending_actions') else [],
        )

        logger.info(f"Partnerships agent completed in {time.time() - start_time:.3f}s")
        return {"agent_results": [agent_result], "completed_agents": ["partnerships"]}

    except Exception as e:
        logger.error(f"Partnerships agent failed: {e}")
        return {
            "agent_results": [AgentResult(
                agent_name="partnerships",
                status="error",
                message=str(e),
            )],
            "completed_agents": ["partnerships"]
        }


@register_agent("marketing")
async def run_marketing_agent(state: GraphState) -> dict:
    """Execute the marketing agent."""
    from src.agents.marketing import marketing_agent

    start_time = time.time()
    logger.info("Marketing agent starting...")

    try:
        result = await marketing_agent.execute(
            prompt=state.user_message,
            context={"event_id": state.event_id} if hasattr(state, 'event_id') else {}
        )

        agent_result = AgentResult(
            agent_name="marketing",
            status="success" if result.success else "error",
            message=result.message,
            data={"execution_time": time.time() - start_time},
            tool_calls=result.tool_calls,
            pending_actions=result.pending_actions if hasattr(result, 'pending_actions') else [],
        )

        logger.info(f"Marketing agent completed in {time.time() - start_time:.3f}s")
        return {"agent_results": [agent_result], "completed_agents": ["marketing"]}

    except Exception as e:
        logger.error(f"Marketing agent failed: {e}")
        return {
            "agent_results": [AgentResult(
                agent_name="marketing",
                status="error",
                message=str(e),
            )],
            "completed_agents": ["marketing"]
        }


@register_agent("finance")
async def run_finance_agent(state: GraphState) -> dict:
    """Execute the finance agent."""
    from src.agents.finance import finance_agent

    start_time = time.time()
    logger.info("Finance agent starting...")

    try:
        result = await finance_agent.execute(
            prompt=state.user_message,
            context={"event_id": state.event_id} if hasattr(state, 'event_id') else {}
        )

        agent_result = AgentResult(
            agent_name="finance",
            status="success" if result.success else "error",
            message=result.message,
            data={"execution_time": time.time() - start_time},
            tool_calls=result.tool_calls,
            pending_actions=result.pending_actions if hasattr(result, 'pending_actions') else [],
        )

        logger.info(f"Finance agent completed in {time.time() - start_time:.3f}s")
        return {"agent_results": [agent_result], "completed_agents": ["finance"]}

    except Exception as e:
        logger.error(f"Finance agent failed: {e}")
        return {
            "agent_results": [AgentResult(
                agent_name="finance",
                status="error",
                message=str(e),
            )],
            "completed_agents": ["finance"]
        }


@register_agent("events")
async def run_events_agent(state: GraphState) -> dict:
    """Execute the events agent."""
    from src.agents.events import events_agent

    start_time = time.time()
    logger.info("Events agent starting...")

    try:
        result = await events_agent.execute(
            prompt=state.user_message,
            context={"event_id": state.event_id} if hasattr(state, 'event_id') else {}
        )

        agent_result = AgentResult(
            agent_name="events",
            status="success" if result.success else "error",
            message=result.message,
            data={"execution_time": time.time() - start_time},
            tool_calls=result.tool_calls,
            pending_actions=result.pending_actions if hasattr(result, 'pending_actions') else [],
        )

        logger.info(f"Events agent completed in {time.time() - start_time:.3f}s")
        return {"agent_results": [agent_result], "completed_agents": ["events"]}

    except Exception as e:
        logger.error(f"Events agent failed: {e}")
        return {
            "agent_results": [AgentResult(
                agent_name="events",
                status="error",
                message=str(e),
            )],
            "completed_agents": ["events"]
        }


@register_agent("developers")
async def run_developers_agent(state: GraphState) -> dict:
    """Execute the developers agent."""
    from src.agents.developers import developers_agent

    start_time = time.time()
    logger.info("Developers agent starting...")

    try:
        result = await developers_agent.execute(
            prompt=state.user_message,
            context={"event_id": state.event_id} if hasattr(state, 'event_id') else {}
        )

        agent_result = AgentResult(
            agent_name="developers",
            status="success" if result.success else "error",
            message=result.message,
            data={"execution_time": time.time() - start_time},
            tool_calls=result.tool_calls,
            pending_actions=result.pending_actions if hasattr(result, 'pending_actions') else [],
        )

        logger.info(f"Developers agent completed in {time.time() - start_time:.3f}s")
        return {"agent_results": [agent_result], "completed_agents": ["developers"]}

    except Exception as e:
        logger.error(f"Developers agent failed: {e}")
        return {
            "agent_results": [AgentResult(
                agent_name="developers",
                status="error",
                message=str(e),
            )],
            "completed_agents": ["developers"]
        }


async def run_agents_parallel(state: GraphState) -> dict:
    """Execute all target agents in parallel using asyncio.gather.

    This node runs all agents specified in target_agents concurrently,
    then merges their results.

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

    # Create tasks for all target agents
    tasks = []
    for agent_name in target_agents:
        if agent_name in AGENT_RUNNERS:
            tasks.append(AGENT_RUNNERS[agent_name](state))
        else:
            logger.warning(f"No runner found for agent: {agent_name}")

    # Execute all agents in parallel
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Merge results
    all_agent_results = []
    all_completed_agents = []
    errors = []

    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logger.error(f"Agent {target_agents[i]} failed: {result}")
            errors.append({
                "agent": target_agents[i],
                "error": str(result),
            })
            all_agent_results.append(AgentResult(
                agent_name=target_agents[i],
                status="error",
                message=f"Agent failed: {str(result)}",
            ))
        else:
            all_agent_results.extend(result.get("agent_results", []))
            all_completed_agents.extend(result.get("completed_agents", []))

    total_time = time.time() - start_time
    logger.info(f"Parallel execution completed in {total_time:.3f}s for {len(target_agents)} agents")

    output = {
        "agent_results": all_agent_results,
        "completed_agents": all_completed_agents,
    }

    if errors:
        output["errors"] = errors

    return output


def should_run_parallel(state: GraphState) -> Literal["parallel_agents", "aggregate"]:
    """Determine if we should run agents in parallel or skip to aggregation."""
    if state.target_agents:
        return "parallel_agents"
    return "aggregate"


async def handle_error(state: GraphState) -> dict:
    """Handle errors that occurred during execution."""
    logger.error(f"Error handler invoked with {len(state.errors)} errors")
    return {"errors": state.errors}


async def aggregate_results(state: GraphState) -> dict:
    """Aggregate results from all executed agents."""
    agent_count = len(state.agent_results)
    completed_count = len(state.completed_agents)
    logger.info(f"Aggregation complete: {agent_count} results from {completed_count} agents")
    return {}


def create_workflow() -> StateGraph:
    """Create and compile the LangGraph workflow with parallel execution."""
    workflow = StateGraph(GraphState)

    workflow.add_node("classify", classify_request)
    workflow.add_node("parallel_agents", run_agents_parallel)
    workflow.add_node("error_handler", handle_error)
    workflow.add_node("aggregate", aggregate_results)

    workflow.set_entry_point("classify")

    workflow.add_conditional_edges(
        "classify",
        should_run_parallel,
        {
            "parallel_agents": "parallel_agents",
            "aggregate": "aggregate",
        },
    )

    workflow.add_edge("parallel_agents", "aggregate")
    workflow.add_edge("error_handler", END)
    workflow.add_edge("aggregate", END)

    return workflow.compile()


# Create the compiled workflow instance
graph = create_workflow()


async def run_workflow(user_message: str, request_id: str = "default") -> GraphState:
    """Run the parallel workflow with a user message."""
    initial_state = GraphState(
        request_id=request_id,
        user_message=user_message,
    )

    result = await graph.ainvoke(initial_state)
    return result
