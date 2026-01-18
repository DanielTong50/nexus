"""Server-Sent Events streaming utilities for real-time agent updates.

Provides SSE streaming for the chat endpoint, allowing the frontend
to receive real-time updates as agents execute.
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime
from typing import AsyncGenerator, Optional

from sse_starlette.sse import EventSourceResponse

from src.models.requests import ChatRequest, StreamEvent
from src.models.state import GraphState

logger = logging.getLogger(__name__)


def create_stream_event(
    event_type: str,
    data: dict,
    agent_name: Optional[str] = None,
) -> str:
    """Create a formatted SSE event string.

    Args:
        event_type: Type of event
        data: Event data payload
        agent_name: Optional agent name

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


async def generate_events(request: ChatRequest) -> AsyncGenerator[str, None]:
    """Generate SSE events for a chat request.

    Yields events as agents process the request:
    - classification: Initial routing decision
    - routing: Agent assignment
    - agent_start: When an agent begins
    - agent_complete: When an agent finishes
    - complete: Final response
    - error: If something goes wrong

    Args:
        request: The chat request to process

    Yields:
        SSE event strings
    """
    request_id = request.request_id or str(uuid.uuid4())

    logger.info(f"Starting stream for request {request_id}")

    try:
        # Import here to avoid circular imports
        from src.graph.classifier import classify_request
        from src.graph.workflow import run_agents_parallel, VALID_AGENTS

        # Create initial state
        state = GraphState(
            request_id=request_id,
            user_message=request.message,
            event_id=request.event_id,
            context=request.context,
        )

        # Classification
        yield create_stream_event(
            "classification",
            {"message": "Analyzing request...", "request_id": request_id},
        )

        classification_result = await classify_request(state)
        target_agents = classification_result.get("target_agents", [])

        yield create_stream_event(
            "routing",
            {
                "agents": target_agents,
                "message": f"Routing to {len(target_agents)} agent(s): {', '.join(target_agents)}"
                if target_agents
                else "No agents needed",
            },
        )

        if not target_agents:
            yield create_stream_event(
                "complete",
                {"message": "No agents needed", "results": [], "request_id": request_id},
            )
            return

        # Update state with targets
        state.target_agents = target_agents

        # Emit agent_start for all
        for agent in target_agents:
            yield create_stream_event(
                "agent_start",
                {"message": f"{agent.title()} agent starting..."},
                agent_name=agent,
            )

        # Run agents in parallel
        result = await run_agents_parallel(state)

        # Emit results
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
        logger.error(f"Stream error: {e}")
        yield create_stream_event(
            "error",
            {"error": str(e), "request_id": request_id},
        )


def create_event_stream(request: ChatRequest) -> EventSourceResponse:
    """Create an SSE response for streaming agent updates.

    Args:
        request: The chat request to process

    Returns:
        EventSourceResponse for SSE streaming
    """
    return EventSourceResponse(
        generate_events(request),
        media_type="text/event-stream",
    )
