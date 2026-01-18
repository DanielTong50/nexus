from pydantic import BaseModel
from typing import Optional, List

class ChatRequest(BaseModel):
    message: str
    thread_id: Optional[str] = None # For conversation persistence
    event_id: Optional[str] = None # Context specific

class ChatResponse(BaseModel):
    response: str
    thread_id: str
