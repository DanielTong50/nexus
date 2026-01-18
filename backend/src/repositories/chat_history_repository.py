"""Repository for chat history and request logging."""

from datetime import datetime
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ASCENDING, DESCENDING

from src.models.chat_history import (
    RequestSummary,
    ChatMessage,
    AgentExecutionLog,
    ConversationThread,
)
from src.repositories.base import BaseRepository
from src.services.database import Collections


class RequestHistoryRepository(BaseRepository[RequestSummary]):
    """Repository for request history/summaries."""

    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, Collections.REQUEST_HISTORY, RequestSummary)

    async def create_indexes(self) -> None:
        """Create indexes for request history collection."""
        await self.collection.create_index([("request_id", ASCENDING)], unique=True)
        await self.collection.create_index([("user_id", ASCENDING), ("created_at", DESCENDING)])
        await self.collection.create_index([("status", ASCENDING)])

    async def find_by_request_id(self, request_id: str) -> Optional[RequestSummary]:
        """Find a request by its request_id."""
        return await self.find_one({"request_id": request_id})

    async def create_request(
        self,
        request_id: str,
        user_message: str,
        user_id: Optional[str] = None,
        event_name: Optional[str] = None,
        context: Optional[dict] = None,
    ) -> RequestSummary:
        """Create a new request record."""
        request = RequestSummary(
            request_id=request_id,
            user_id=user_id,
            user_message=user_message,
            event_name=event_name,
            context=context or {},
            status="pending",
        )
        return await self.create(request)

    async def update_classification(
        self,
        request_id: str,
        target_agents: list[str],
        classification_result: dict,
    ) -> Optional[RequestSummary]:
        """Update request with classification results."""
        return await self.update_one(
            {"request_id": request_id},
            {
                "status": "executing",
                "target_agents": target_agents,
                "classification_result": classification_result,
            },
        )

    async def complete_request(
        self,
        request_id: str,
        completed_agents: list[str],
        pending_approvals: Optional[list[str]] = None,
        error: Optional[str] = None,
    ) -> Optional[RequestSummary]:
        """Mark a request as completed."""
        now = datetime.utcnow()
        request = await self.find_by_request_id(request_id)
        if not request:
            return None

        duration_ms = None
        if request.started_at:
            duration_ms = int((now - request.started_at).total_seconds() * 1000)

        update_data = {
            "status": "error" if error else "completed",
            "completed_agents": completed_agents,
            "completed_at": now,
            "duration_ms": duration_ms,
        }
        if pending_approvals:
            update_data["pending_approvals"] = pending_approvals
        if error:
            update_data["error_message"] = error

        return await self.update_one({"request_id": request_id}, update_data)

    async def get_user_history(
        self,
        user_id: str,
        limit: int = 50,
        skip: int = 0,
    ) -> list[RequestSummary]:
        """Get request history for a user."""
        return await self.find_many(
            {"user_id": user_id},
            sort=[("created_at", DESCENDING)],
            limit=limit,
            skip=skip,
        )

    async def get_recent_requests(
        self,
        limit: int = 100,
        status: Optional[str] = None,
    ) -> list[RequestSummary]:
        """Get recent requests, optionally filtered by status."""
        query = {}
        if status:
            query["status"] = status
        return await self.find_many(
            query,
            sort=[("created_at", DESCENDING)],
            limit=limit,
        )


class ChatMessageRepository(BaseRepository[ChatMessage]):
    """Repository for chat messages."""

    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, Collections.CHAT_MESSAGES, ChatMessage)

    async def create_indexes(self) -> None:
        """Create indexes for chat messages collection."""
        await self.collection.create_index(
            [("request_id", ASCENDING), ("created_at", ASCENDING)]
        )

    async def add_message(
        self,
        request_id: str,
        role: str,
        content: str,
        agent_name: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> ChatMessage:
        """Add a chat message."""
        message = ChatMessage(
            request_id=request_id,
            role=role,
            content=content,
            agent_name=agent_name,
            metadata=metadata or {},
        )
        return await self.create(message)

    async def get_messages_for_request(self, request_id: str) -> list[ChatMessage]:
        """Get all messages for a request in chronological order."""
        return await self.find_many(
            {"request_id": request_id},
            sort=[("created_at", ASCENDING)],
        )


class AgentExecutionRepository(BaseRepository[AgentExecutionLog]):
    """Repository for agent execution logs."""

    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, Collections.AGENT_EXECUTIONS, AgentExecutionLog)

    async def create_indexes(self) -> None:
        """Create indexes for agent executions collection."""
        await self.collection.create_index(
            [("request_id", ASCENDING), ("agent_name", ASCENDING)]
        )
        await self.collection.create_index([("status", ASCENDING)])

    async def log_agent_start(
        self,
        request_id: str,
        agent_name: str,
    ) -> AgentExecutionLog:
        """Log the start of an agent execution."""
        log = AgentExecutionLog(
            request_id=request_id,
            agent_name=agent_name,
            status="started",
        )
        return await self.create(log)

    async def log_agent_complete(
        self,
        request_id: str,
        agent_name: str,
        message: str,
        data: Optional[dict] = None,
        tool_calls: Optional[list[dict]] = None,
        pending_actions: Optional[list[dict]] = None,
    ) -> Optional[AgentExecutionLog]:
        """Log the completion of an agent execution."""
        now = datetime.utcnow()

        # Find the existing log
        existing = await self.find_one(
            {"request_id": request_id, "agent_name": agent_name}
        )

        duration_ms = None
        if existing and existing.started_at:
            duration_ms = int((now - existing.started_at).total_seconds() * 1000)

        return await self.update_one(
            {"request_id": request_id, "agent_name": agent_name},
            {
                "status": "completed",
                "message": message,
                "data": data,
                "tool_calls": tool_calls or [],
                "pending_actions": pending_actions or [],
                "completed_at": now,
                "duration_ms": duration_ms,
            },
        )

    async def log_agent_error(
        self,
        request_id: str,
        agent_name: str,
        error_message: str,
    ) -> Optional[AgentExecutionLog]:
        """Log an agent execution error."""
        now = datetime.utcnow()

        existing = await self.find_one(
            {"request_id": request_id, "agent_name": agent_name}
        )

        duration_ms = None
        if existing and existing.started_at:
            duration_ms = int((now - existing.started_at).total_seconds() * 1000)

        return await self.update_one(
            {"request_id": request_id, "agent_name": agent_name},
            {
                "status": "error",
                "error_message": error_message,
                "completed_at": now,
                "duration_ms": duration_ms,
            },
        )

    async def get_executions_for_request(
        self, request_id: str
    ) -> list[AgentExecutionLog]:
        """Get all agent executions for a request."""
        return await self.find_many(
            {"request_id": request_id},
            sort=[("created_at", ASCENDING)],
        )


class ChatHistoryRepository:
    """Facade for all chat history operations."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.requests = RequestHistoryRepository(db)
        self.messages = ChatMessageRepository(db)
        self.executions = AgentExecutionRepository(db)

    async def create_indexes(self) -> None:
        """Create all indexes for chat history collections."""
        await self.requests.create_indexes()
        await self.messages.create_indexes()
        await self.executions.create_indexes()

    async def start_request(
        self,
        request_id: str,
        user_message: str,
        user_id: Optional[str] = None,
        event_name: Optional[str] = None,
        context: Optional[dict] = None,
    ) -> RequestSummary:
        """Start tracking a new request."""
        request = await self.requests.create_request(
            request_id=request_id,
            user_message=user_message,
            user_id=user_id,
            event_name=event_name,
            context=context,
        )
        # Also log the user message
        await self.messages.add_message(
            request_id=request_id,
            role="user",
            content=user_message,
        )
        return request

    async def record_classification(
        self,
        request_id: str,
        target_agents: list[str],
        classification_result: dict,
    ) -> Optional[RequestSummary]:
        """Record classification results for a request."""
        return await self.requests.update_classification(
            request_id, target_agents, classification_result
        )

    async def start_agent(
        self,
        request_id: str,
        agent_name: str,
    ) -> AgentExecutionLog:
        """Record the start of an agent execution."""
        return await self.executions.log_agent_start(request_id, agent_name)

    async def complete_agent(
        self,
        request_id: str,
        agent_name: str,
        message: str,
        data: Optional[dict] = None,
        tool_calls: Optional[list[dict]] = None,
        pending_actions: Optional[list[dict]] = None,
    ) -> Optional[AgentExecutionLog]:
        """Record the completion of an agent execution."""
        log = await self.executions.log_agent_complete(
            request_id, agent_name, message, data, tool_calls, pending_actions
        )
        # Also log the agent response as a message
        await self.messages.add_message(
            request_id=request_id,
            role="agent",
            content=message,
            agent_name=agent_name,
            metadata={"data": data, "tool_calls": tool_calls},
        )
        return log

    async def fail_agent(
        self,
        request_id: str,
        agent_name: str,
        error_message: str,
    ) -> Optional[AgentExecutionLog]:
        """Record an agent execution failure."""
        return await self.executions.log_agent_error(request_id, agent_name, error_message)

    async def complete_request(
        self,
        request_id: str,
        completed_agents: list[str],
        pending_approvals: Optional[list[str]] = None,
        error: Optional[str] = None,
    ) -> Optional[RequestSummary]:
        """Complete and finalize a request."""
        return await self.requests.complete_request(
            request_id, completed_agents, pending_approvals, error
        )

    async def get_full_history(
        self,
        request_id: str,
    ) -> dict:
        """Get the full history of a request including all messages and executions."""
        request = await self.requests.find_by_request_id(request_id)
        messages = await self.messages.get_messages_for_request(request_id)
        executions = await self.executions.get_executions_for_request(request_id)

        return {
            "request": request.model_dump() if request else None,
            "messages": [m.model_dump() for m in messages],
            "executions": [e.model_dump() for e in executions],
        }
