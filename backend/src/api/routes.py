from fastapi import APIRouter, Depends, HTTPException
from sse_starlette.sse import EventSourceResponse
from src.services.database import get_db
from src.models.requests import ChatRequest
from src.api.streaming import event_generator

router = APIRouter()

@router.get("/health")
async def health_check(db = Depends(get_db)):
    """Checks API status and DB connection"""
    if db is None:
        raise HTTPException(status_code=503, detail="Database not connected")
    return {"status": "ok", "database": "connected"}

@router.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """
    Main entry point for Agent Chat.
    Returns a StreamingResponse (SSE).
    """
    generator = event_generator(request.message)
    return EventSourceResponse(generator)
