from typing import TYPE_CHECKING

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import ASCENDING, DESCENDING
from config.settings import settings
import logging

if TYPE_CHECKING:
    from src.repositories.base import BaseRepository

logger = logging.getLogger(__name__)


# Collection names as constants
class Collections:
    """MongoDB collection names."""

    APPROVALS = "approvals"
    APPROVAL_HISTORY = "approval_history"
    REQUEST_HISTORY = "request_history"
    CHAT_MESSAGES = "chat_messages"
    AGENT_EXECUTIONS = "agent_executions"
    USER_SESSIONS = "user_sessions"
    USER_PROFILES = "user_profiles"
    PARTNERSHIPS_SPONSORS = "partnerships_sponsors"
    PARTNERSHIPS_JUDGES = "partnerships_judges"
    PARTNERSHIPS_MENTORS = "partnerships_mentors"
    EVENT_LOGISTICS = "event_logistics"
    ROOM_BOOKINGS = "room_bookings"
    BUDGET_TRANSACTIONS = "budget_transactions"


class Database:
    """MongoDB database connection and management."""

    client: AsyncIOMotorClient = None
    db: AsyncIOMotorDatabase = None
    _repositories: dict[str, "BaseRepository"] = {}

    def connect(self):
        """Establish connection to MongoDB Atlas."""
        try:
            self.client = AsyncIOMotorClient(settings.MONGO_URI)
            self.db = self.client[settings.DB_NAME]
            logger.info("MongoDB client initialized.")
        except Exception as e:
            logger.error(f"Failed to initialize MongoDB client: {e}")
            raise e

    async def close(self):
        """Close connection."""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed.")

    async def ping(self):
        """Health check."""
        try:
            await self.client.admin.command("ping")
            return True
        except Exception as e:
            logger.error(f"MongoDB Ping Failed: {e}")
            return False

    async def create_indexes(self) -> None:
        """Create all collection indexes on startup."""
        logger.info("Creating MongoDB indexes...")

        try:
            # Approvals collection indexes
            await self.db[Collections.APPROVALS].create_index(
                [("approval_id", ASCENDING)], unique=True
            )
            await self.db[Collections.APPROVALS].create_index(
                [("status", ASCENDING), ("created_at", DESCENDING)]
            )
            await self.db[Collections.APPROVALS].create_index([("expires_at", ASCENDING)])
            await self.db[Collections.APPROVALS].create_index([("request_id", ASCENDING)])

            # Approval history indexes
            await self.db[Collections.APPROVAL_HISTORY].create_index(
                [("approval_id", ASCENDING), ("created_at", DESCENDING)]
            )

            # Request history indexes
            await self.db[Collections.REQUEST_HISTORY].create_index(
                [("request_id", ASCENDING)], unique=True
            )
            await self.db[Collections.REQUEST_HISTORY].create_index(
                [("user_id", ASCENDING), ("created_at", DESCENDING)]
            )

            # Chat messages indexes
            await self.db[Collections.CHAT_MESSAGES].create_index(
                [("request_id", ASCENDING), ("created_at", ASCENDING)]
            )

            # Agent executions indexes
            await self.db[Collections.AGENT_EXECUTIONS].create_index(
                [("request_id", ASCENDING), ("agent_name", ASCENDING)]
            )

            # User sessions indexes
            await self.db[Collections.USER_SESSIONS].create_index(
                [("session_id", ASCENDING)], unique=True
            )
            await self.db[Collections.USER_SESSIONS].create_index(
                [("user_id", ASCENDING), ("is_active", ASCENDING)]
            )
            await self.db[Collections.USER_SESSIONS].create_index([("expires_at", ASCENDING)])

            # User profiles indexes
            await self.db[Collections.USER_PROFILES].create_index(
                [("user_id", ASCENDING)], unique=True
            )
            await self.db[Collections.USER_PROFILES].create_index(
                [("email", ASCENDING)], unique=True
            )

            # Partnership indexes (for all partnership types)
            for collection_name in [
                Collections.PARTNERSHIPS_SPONSORS,
                Collections.PARTNERSHIPS_JUDGES,
                Collections.PARTNERSHIPS_MENTORS,
            ]:
                await self.db[collection_name].create_index([("company", ASCENDING)])
                await self.db[collection_name].create_index([("status", ASCENDING)])
                await self.db[collection_name].create_index([("contact_email", ASCENDING)])

            # Event logistics indexes
            await self.db[Collections.EVENT_LOGISTICS].create_index(
                [("event_name", ASCENDING)], unique=True
            )

            # Room bookings indexes
            await self.db[Collections.ROOM_BOOKINGS].create_index(
                [("event_name", ASCENDING), ("date", ASCENDING), ("room_name", ASCENDING)]
            )

            # Budget transactions indexes
            await self.db[Collections.BUDGET_TRANSACTIONS].create_index(
                [("event_name", ASCENDING), ("created_at", DESCENDING)]
            )

            logger.info("MongoDB indexes created successfully.")

        except Exception as e:
            logger.error(f"Failed to create indexes: {e}")
            raise e

    def get_collection(self, name: str):
        """Get a MongoDB collection by name."""
        return self.db[name]


db_service = Database()


async def get_db() -> AsyncIOMotorDatabase:
    """Dependency for Routes."""
    return db_service.db
