"""Async MongoDB database service.

Provides a singleton connection to MongoDB Atlas using Motor.
"""

import logging
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from config.settings import settings

logger = logging.getLogger(__name__)

# Singleton client instance
_client: Optional[AsyncIOMotorClient] = None
_db: Optional[AsyncIOMotorDatabase] = None


async def connect_to_mongo() -> None:
    """Connect to MongoDB Atlas.

    Called during application startup.
    """
    global _client, _db

    logger.info(f"Connecting to MongoDB: {settings.db_name}")

    _client = AsyncIOMotorClient(
        settings.mongo_uri,
        maxPoolSize=10,
        minPoolSize=1,
        serverSelectionTimeoutMS=5000,
    )
    _db = _client[settings.db_name]

    # Verify connection
    await ping()
    logger.info("MongoDB connection established")


async def close_mongo_connection() -> None:
    """Close MongoDB connection.

    Called during application shutdown.
    """
    global _client, _db

    if _client:
        logger.info("Closing MongoDB connection")
        _client.close()
        _client = None
        _db = None


async def ping() -> bool:
    """Ping the database to verify connection.

    Returns:
        True if connection is healthy
    """
    if _client is None:
        raise ConnectionError("MongoDB client not initialized")

    try:
        await _client.admin.command("ping")
        return True
    except Exception as e:
        logger.error(f"MongoDB ping failed: {e}")
        raise


def get_database() -> AsyncIOMotorDatabase:
    """Get the database instance.

    Returns:
        AsyncIOMotorDatabase instance

    Raises:
        ConnectionError: If database not connected
    """
    if _db is None:
        raise ConnectionError("Database not connected. Call connect_to_mongo() first.")
    return _db


async def get_db() -> AsyncIOMotorDatabase:
    """FastAPI dependency for database access.

    Returns:
        AsyncIOMotorDatabase instance
    """
    return get_database()


# Collection helpers
def get_collection(name: str):
    """Get a collection by name.

    Args:
        name: Collection name

    Returns:
        AsyncIOMotorCollection
    """
    db = get_database()
    return db[name]


# Common collections
def events_collection():
    """Get the events collection."""
    return get_collection("events")


def requests_collection():
    """Get the requests collection."""
    return get_collection("requests")


def approvals_collection():
    """Get the approvals collection."""
    return get_collection("approvals")
