"""Server-Sent Events streaming utilities."""

import json
from typing import AsyncGenerator

from sse_starlette.sse import EventSourceResponse

from src.models.requests import ChatRequest, StreamEvent


async def generate_events(request: ChatRequest) -> AsyncGenerator[str, None]:
    """Generate SSE events for a chat request.

    Yields events as agents process the request, including:
    - classification: Initial routing decision
    - agent_start: When an agent begins processing
    - agent_update: Progress updates from agents
    - agent_complete: When an agent finishes
    - complete: Final aggregated response
    - error: If something goes wrong
    """
    # TODO: Implement actual graph streaming

    # Example event structure
    yield json.dumps(
        StreamEvent(
            event_type="classification",
            data={"agents": [], "message": request.message},
        ).model_dump()
    )

    yield json.dumps(
        StreamEvent(
            event_type="complete",
            data={"message": "Processing complete", "results": []},
        ).model_dump()
    )


def create_event_stream(request: ChatRequest) -> EventSourceResponse:
    """Create an SSE response for streaming agent updates."""
    return EventSourceResponse(
        generate_events(request),
        media_type="text/event-stream",
    )
