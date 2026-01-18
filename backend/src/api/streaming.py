"""Server-Sent Events streaming utilities for real-time agent updates.

This module provides SSE streaming for the chat endpoint, allowing
the frontend to receive real-time updates as agents execute.
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime
from typing import AsyncGenerator, Optional

from sse_starlette.sse import EventSourceResponse

from src.graph.workflow import run_agents_parallel, AGENT_RUNNERS
from src.graph.classifier import classify_request
from src.models.requests import ChatRequest, StreamEvent, PendingApproval
from src.models.state import GraphState, AgentResult

logger = logging.getLogger(__name__)

# In-memory store for pending approvals (replace with Redis/DB in production)
PENDING_APPROVALS: dict[str, PendingApproval] = {}

# Actions that require approval
ACTIONS_REQUIRING_APPROVAL = [
    "draft_mou",
    "generate_invoice",
    "schedule_instagram_post",
    "schedule_linkedin_post",
    "announce_to_slack",
]


def create_stream_event(
    event_type: str,
    data: dict,
    agent_name: Optional[str] = None,
) -> str:
    """Create a formatted SSE event string.

    Args:
        event_type: Type of event (classification, agent_start, etc.)
        data: Event data payload
        agent_name: Optional agent name for agent-specific events

    Returns:
        JSON string for SSE
    """
    event = StreamEvent(
        event_type=event_type,
        data=data,
        agent_name=agent_name,
        timestamp=datetime.utcnow(),
    )
    return json.dumps(event.model_dump(), default=str)


async def stream_classification(state: GraphState) -> tuple[dict, list[str]]:
    """Run classification and return result with target agents.

    Args:
        state: Initial graph state

    Returns:
        Tuple of (classification_result, target_agents)
    """
    result = await classify_request(state)
    target_agents = result.get("target_agents", [])
    return result, target_agents


async def stream_agent_execution(
    state: GraphState,
    agent_name: str,
) -> AsyncGenerator[str, None]:
    """Stream events for a single agent's execution.

    Args:
        state: Current graph state
        agent_name: Name of agent to execute

    Yields:
        SSE event strings
    """
    # Agent start event
    yield create_stream_event(
        "agent_start",
        {"message": f"{agent_name.title()} agent starting..."},
        agent_name=agent_name,
    )

    try:
        if agent_name in AGENT_RUNNERS:
            runner = AGENT_RUNNERS[agent_name]
            result = await runner(state)

            agent_results = result.get("agent_results", [])
            for agent_result in agent_results:
                # Check for tool calls
                if hasattr(agent_result, "tool_calls") and agent_result.tool_calls:
                    for tool_call in agent_result.tool_calls:
                        yield create_stream_event(
                            "agent_tool_call",
                            {
                                "tool": tool_call.get("name", "unknown"),
                                "status": "executing",
                            },
                            agent_name=agent_name,
                        )

                # Agent complete
                yield create_stream_event(
                    "agent_complete",
                    {
                        "status": agent_result.status,
                        "message": agent_result.message,
                        "data": agent_result.data,
                    },
                    agent_name=agent_name,
                )
        else:
            yield create_stream_event(
                "agent_error",
                {"error": f"Agent {agent_name} not found"},
                agent_name=agent_name,
            )

    except Exception as e:
        logger.error(f"Agent {agent_name} error: {e}")
        yield create_stream_event(
            "agent_error",
            {"error": str(e)},
            agent_name=agent_name,
        )


async def generate_events(request: ChatRequest) -> AsyncGenerator[str, None]:
    """Generate SSE events for a chat request.

    This is the main streaming function that:
    1. Classifies the request
    2. Routes to agents
    3. Streams agent execution updates
    4. Handles approvals if needed
    5. Returns final results

    Args:
        request: The chat request to process

    Yields:
        SSE event strings in real-time
    """
    request_id = request.request_id or str(uuid.uuid4())

    logger.info(f"Starting stream for request {request_id}: {request.message[:50]}...")

    # Create initial state
    state = GraphState(
        request_id=request_id,
        user_message=request.message,
        context=request.context,
    )

    try:
        # Step 1: Classification
        yield create_stream_event(
            "classification",
            {"message": "Analyzing request...", "request_id": request_id},
        )

        classification_result, target_agents = await stream_classification(state)

        yield create_stream_event(
            "routing",
            {
                "agents": target_agents,
                "message": f"Routing to {len(target_agents)} agent(s): {', '.join(target_agents)}" if target_agents else "No agents needed",
            },
        )

        if not target_agents:
            yield create_stream_event(
                "complete",
                {
                    "message": "No agents were needed for this request",
                    "results": [],
                    "request_id": request_id,
                },
            )
            return

        # Step 2: Execute agents in parallel, streaming updates
        # Update state with target agents
        state.target_agents = target_agents

        # Stream individual agent updates
        all_results: list[dict] = []
        pending_approval_ids: list[str] = []

        # Execute agents and stream their updates
        for agent_name in target_agents:
            async for event in stream_agent_execution(state, agent_name):
                yield event

                # Parse the event to check for results
                try:
                    event_data = json.loads(event)
                    if event_data.get("event_type") == "agent_complete":
                        all_results.append({
                            "agent_name": agent_name,
                            **event_data.get("data", {}),
                        })
                except json.JSONDecodeError:
                    pass

        # Step 3: Check for actions requiring approval
        for result in all_results:
            if result.get("data") and result["data"].get("action_type") in ACTIONS_REQUIRING_APPROVAL:
                approval_id = str(uuid.uuid4())
                approval = PendingApproval(
                    approval_id=approval_id,
                    request_id=request_id,
                    agent_name=result.get("agent_name", "unknown"),
                    action_type=result["data"]["action_type"],
                    action_description=result["data"].get("description", "Action requires approval"),
                    action_data=result["data"],
                )
                PENDING_APPROVALS[approval_id] = approval
                pending_approval_ids.append(approval_id)

                yield create_stream_event(
                    "approval_required",
                    {
                        "approval_id": approval_id,
                        "agent_name": approval.agent_name,
                        "action_type": approval.action_type,
                        "description": approval.action_description,
                    },
                )

        # Step 4: Complete
        yield create_stream_event(
            "complete",
            {
                "message": "All agents completed",
                "request_id": request_id,
                "agents_invoked": target_agents,
                "results": all_results,
                "pending_approvals": pending_approval_ids,
            },
        )

    except Exception as e:
        logger.error(f"Stream error for request {request_id}: {e}")
        yield create_stream_event(
            "error",
            {
                "error": str(e),
                "request_id": request_id,
            },
        )


async def generate_events_parallel(request: ChatRequest) -> AsyncGenerator[str, None]:
    """Generate SSE events with true parallel agent execution.

    This version uses asyncio.gather for parallel execution while
    still streaming updates.

    Args:
        request: The chat request to process

    Yields:
        SSE event strings
    """
    request_id = request.request_id or str(uuid.uuid4())

    state = GraphState(
        request_id=request_id,
        user_message=request.message,
        context=request.context,
    )

    try:
        # Classification
        yield create_stream_event(
            "classification",
            {"message": "Analyzing request...", "request_id": request_id},
        )

        classification_result, target_agents = await stream_classification(state)
        state.target_agents = target_agents

        yield create_stream_event(
            "routing",
            {
                "agents": target_agents,
                "message": f"Routing to {len(target_agents)} agent(s)",
            },
        )

        if not target_agents:
            yield create_stream_event("complete", {"message": "No agents needed", "results": []})
            return

        # Emit agent_start for all agents
        for agent in target_agents:
            yield create_stream_event(
                "agent_start",
                {"message": f"{agent.title()} agent starting..."},
                agent_name=agent,
            )

        # Run all agents in parallel
        result = await run_agents_parallel(state)

        # Emit results for each agent
        for agent_result in result.get("agent_results", []):
            yield create_stream_event(
                "agent_complete",
                {
                    "status": agent_result.status,
                    "message": agent_result.message,
                    "data": agent_result.data,
                },
                agent_name=agent_result.agent_name,
            )

        # Complete
        yield create_stream_event(
            "complete",
            {
                "message": "All agents completed",
                "request_id": request_id,
                "agents_invoked": result.get("completed_agents", []),
                "results": [r.model_dump() for r in result.get("agent_results", [])],
            },
        )

    except Exception as e:
        logger.error(f"Parallel stream error: {e}")
        yield create_stream_event("error", {"error": str(e), "request_id": request_id})


def create_event_stream(request: ChatRequest, parallel: bool = True) -> EventSourceResponse:
    """Create an SSE response for streaming agent updates.

    Args:
        request: The chat request to process
        parallel: Whether to use parallel execution (default: True)

    Returns:
        EventSourceResponse for SSE streaming
    """
    generator = generate_events_parallel if parallel else generate_events
    return EventSourceResponse(
        generator(request),
        media_type="text/event-stream",
    )


def get_pending_approval(approval_id: str) -> Optional[PendingApproval]:
    """Get a pending approval by ID."""
    return PENDING_APPROVALS.get(approval_id)


def get_all_pending_approvals() -> list[PendingApproval]:
    """Get all pending approvals."""
    return [a for a in PENDING_APPROVALS.values() if a.status == "pending"]


def update_approval_status(approval_id: str, status: str) -> Optional[PendingApproval]:
    """Update the status of an approval."""
    if approval_id in PENDING_APPROVALS:
        PENDING_APPROVALS[approval_id].status = status
        return PENDING_APPROVALS[approval_id]
    return None
