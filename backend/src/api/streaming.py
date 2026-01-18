import json
import asyncio
from typing import AsyncGenerator

async def event_generator(request_input: str) -> AsyncGenerator[str, None]:
    """
    Simulates streaming response.
    In Phase 2, this will yield updates from the LangGraph workflow.
    """

    # STUB: Mocking the stream for infrastructure testing
    stages = [
        {"type": "status", "content": "Initializing Nexus Core..."},
        {"type": "thought", "content": "Classifying intent via Gemini 1.5 Pro..."},
        {"type": "chunk", "content": "Hello! "},
        {"type": "chunk", "content": "The backend system "},
        {"type": "chunk", "content": "is now online "},
        {"type": "chunk", "content": "and connected to MongoDB. "},
        {"type": "done", "content": ""}
    ]

    for stage in stages:
        if await asyncio.sleep(0.5): pass # Simulate latency
        yield json.dumps(stage)
