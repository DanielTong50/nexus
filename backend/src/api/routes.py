"""API route definitions."""

from fastapi import APIRouter, HTTPException

from src.api.streaming import create_event_stream
from src.models.requests import ChatRequest, ChatResponse

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def process_chat(request: ChatRequest) -> ChatResponse:
    """Process a chat request and return agent responses.

    This endpoint handles synchronous requests where the full response
    is returned after all agents complete their work.
    """
    # TODO: Implement graph execution
    return ChatResponse(
        request_id=request.request_id or "generated-id",
        message=request.message,
        agents_invoked=[],
        results=[],
    )


@router.post("/chat/stream")
async def process_chat_stream(request: ChatRequest):
    """Process a chat request with Server-Sent Events streaming.

    This endpoint streams agent updates in real-time as they execute,
    providing immediate feedback to the user.
    
    """
    return create_event_stream(request)


@router.get("/agents")
async def list_agents() -> dict:
    """List available agents and their capabilities."""
    return {
        "agents": [
            {
                "name": "partnerships",
                "description": "Handles sponsors, judges, mentors, and partner outreach",
            },
            {
                "name": "marketing",
                "description": "Handles social media, content creation, and promotions",
            },
            {
                "name": "finance",
                "description": "Handles budgets, expenses, and financial tracking",
            },
            {
                "name": "events",
                "description": "Handles event logistics, scheduling, and coordination",
            },
            {
                "name": "developers",
                "description": "Handles technical tasks, GitHub, and development workflows",
            },
        ]
    }
