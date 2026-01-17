"""MongoDB database connection and utilities."""

import logging
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from config.settings import settings

logger = logging.getLogger(__name__)


class Database:
    """MongoDB database connection manager."""

    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None


db = Database()


async def connect_to_mongo() -> None:
    """Establish connection to MongoDB."""
    logger.info("Connecting to MongoDB...")
    try:
        db.client = AsyncIOMotorClient(
            settings.mongodb_uri,
            serverSelectionTimeoutMS=5000,
        )
        db.db = db.client[settings.mongodb_database]

        # Verify connection
        await db.client.admin.command("ping")
        logger.info(f"Connected to MongoDB database: {settings.mongodb_database}")
    except Exception as e:
        logger.warning(f"Failed to connect to MongoDB: {e}")
        if settings.is_production:
            raise
        logger.warning("Running without MongoDB connection (development mode)")


async def close_mongo_connection() -> None:
    """Close MongoDB connection."""
    if db.client:
        logger.info("Closing MongoDB connection...")
        db.client.close()
        logger.info("MongoDB connection closed")


def get_database() -> AsyncIOMotorDatabase:
    """Get the database instance.

    Returns:
        The MongoDB database instance.

    Raises:
        RuntimeError: If database is not connected.
    """
    if db.db is None:
        raise RuntimeError("Database not connected. Call connect_to_mongo() first.")
    return db.db


def get_collection(name: str):
    """Get a collection from the database.

    Args:
        name: The collection name.

    Returns:
        The MongoDB collection.
    """
    return get_database()[name]
