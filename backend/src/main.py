"""FastAPI application entry point.

Nexus Backend - AI-native event production platform.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.settings import settings
from src.api.routes import router
from src.services.database import close_mongo_connection, connect_to_mongo

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application startup and shutdown events."""
    # Startup
    logger.info(f"Starting Nexus Backend ({settings.environment})")
    logger.info(f"Active agent provider: {settings.active_agent_provider}")

    try:
        await connect_to_mongo()
        logger.info("Database connected")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        # Continue anyway for development

    yield

    # Shutdown
    logger.info("Shutting down Nexus Backend")
    await close_mongo_connection()


# Create FastAPI app
app = FastAPI(
    title="Nexus API",
    description="AI-native event production platform API",
    version="0.1.0",
    debug=settings.debug,
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins if not settings.debug else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router, prefix="/api")


@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint."""
    from src.services.database import ping

    db_status = "connected"
    try:
        await ping()
    except Exception:
        db_status = "disconnected"

    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "app": settings.app_name,
        "environment": settings.environment,
        "database": db_status,
        "llm_provider": settings.active_agent_provider,
    }


@app.get("/")
async def root():
    """Redirect to API documentation."""
    from fastapi.responses import RedirectResponse

    return RedirectResponse(url="/docs")


# Run with uvicorn
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
