"""LangGraph workflow definition for multi-agent orchestration.

This module defines the workflow graph that:
1. Classifies user requests
2. Routes to appropriate agents
3. Executes agents in parallel using asyncio.gather
4. Aggregates results
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
    """Execute the partnerships agent."""
    start_time = time.time()
    # Simulate some async work
    await asyncio.sleep(0.01)
    
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
            # Create error result for failed agent
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
    """Determine if we should run agents in parallel or skip to aggregation.

    Args:
        state: Current graph state

    Returns:
        "parallel_agents" if there are agents to run, "aggregate" otherwise
    """
    if state.target_agents:
        return "parallel_agents"
    return "aggregate"


async def handle_error(state: GraphState) -> dict:
    """Handle errors that occurred during execution."""
    logger.error(f"Error handler invoked with {len(state.errors)} errors")
    return {"errors": state.errors}


async def aggregate_results(state: GraphState) -> dict:
    """Aggregate results from all executed agents.

    Args:
        state: Current graph state with agent_results populated

    Returns:
        Empty dict (results already in state)
    """
    agent_count = len(state.agent_results)
    completed_count = len(state.completed_agents)
    logger.info(f"Aggregation complete: {agent_count} results from {completed_count} agents")
    return {}


def create_workflow() -> StateGraph:
    """Create and compile the LangGraph workflow with parallel execution.

    The workflow structure:
    1. classify: Analyze request and determine target agents
    2. parallel_agents: Execute all target agents concurrently
    3. aggregate: Merge and finalize results

    Returns:
        Compiled StateGraph ready for execution.
    """
    workflow = StateGraph(GraphState)

    # Add nodes
    workflow.add_node("classify", classify_request)
    workflow.add_node("parallel_agents", run_agents_parallel)
    workflow.add_node("error_handler", handle_error)
    workflow.add_node("aggregate", aggregate_results)

    # Set entry point
    workflow.set_entry_point("classify")

    # Route from classifier to parallel execution or aggregate
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


def create_sequential_workflow() -> StateGraph:
    """Create workflow with sequential agent execution (for comparison/fallback).

    Returns:
        Compiled StateGraph with sequential execution.
    """
    workflow = StateGraph(GraphState)

    # Add nodes
    workflow.add_node("classify", classify_request)
    workflow.add_node("partnerships", run_partnerships_agent)
    workflow.add_node("marketing", run_marketing_agent)
    workflow.add_node("finance", run_finance_agent)
    workflow.add_node("events", run_events_agent)
    workflow.add_node("developers", run_developers_agent)
    workflow.add_node("error_handler", handle_error)
    workflow.add_node("aggregate", aggregate_results)

    # Set entry point
    workflow.set_entry_point("classify")

    # Add conditional edges from classifier (sequential - first agent only)
    workflow.add_conditional_edges(
        "classify",
        route_to_agents,
        {
            "partnerships": "partnerships",
            "marketing": "marketing",
            "finance": "finance",
            "events": "events",
            "developers": "developers",
            "aggregate": "aggregate",
        },
    )

    # Connect agent nodes to aggregation
    for agent in ["partnerships", "marketing", "finance", "events", "developers"]:
        workflow.add_edge(agent, "aggregate")

    workflow.add_edge("error_handler", END)
    workflow.add_edge("aggregate", END)

    return workflow.compile()


# Create the compiled workflow instances
graph = create_workflow()  # Default: parallel execution
sequential_graph = create_sequential_workflow()  # For comparison


# Convenience function for running the parallel workflow
async def run_workflow(user_message: str, request_id: str = "default") -> GraphState:
    """Run the parallel workflow with a user message.

    Args:
        user_message: The user's input message
        request_id: Unique identifier for this request

    Returns:
        Final GraphState with all results
    """
    initial_state = GraphState(
        request_id=request_id,
        user_message=user_message,
    )

    result = await graph.ainvoke(initial_state)
    return result
