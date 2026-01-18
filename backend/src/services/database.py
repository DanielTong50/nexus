from motor.motor_asyncio import AsyncIOMotorClient
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

class Database:
    client: AsyncIOMotorClient = None
    db = None

    def connect(self):
        """Establish connection to MongoDB Atlas"""
        try:
            self.client = AsyncIOMotorClient(settings.MONGO_URI)
            self.db = self.client[settings.DB_NAME]
            logger.info("MongoDB client initialized.")
        except Exception as e:
            logger.error(f"Failed to initialize MongoDB client: {e}")
            raise e

    async def close(self):
        """Close connection"""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed.")

    async def ping(self):
        """Health check"""
        try:
            await self.client.admin.command('ping')
            return True
        except Exception as e:
            logger.error(f"MongoDB Ping Failed: {e}")
            return False

db_service = Database()

async def get_db():
    """Dependency for Routes"""
    return db_service.db
