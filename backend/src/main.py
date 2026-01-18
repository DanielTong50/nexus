from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.settings import settings
from src.services.database import db_service
from src.api.routes import router as api_router
import logging

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nexus")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events: DB Connect on start, Close on shutdown"""
    logger.info("Starting Nexus Backend...")
    db_service.connect()

    # Verify Connection
    is_connected = await db_service.ping()
    if is_connected:
        logger.info("✅ Connected to MongoDB Atlas")

        # Create database indexes
        try:
            await db_service.create_indexes()
            logger.info("✅ MongoDB indexes created/verified")
        except Exception as e:
            logger.error(f"⚠️ Failed to create indexes: {e}")
    else:
        logger.error("❌ Failed to connect to MongoDB Atlas")

    yield

    await db_service.close()
    logger.info("Nexus Backend Shutdown.")

app = FastAPI(
    title="Nexus Backend API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Setup - Allow Netlify, Railway domains, and custom domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS + ["https://nexusapp.tech", "https://www.nexusapp.tech"],
    allow_origin_regex=r"https://.*\.(netlify\.app|railway\.app|nexusapp\.tech)$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routes
app.include_router(api_router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
