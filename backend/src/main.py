"""FastAPI application entry point."""
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.settings import settings
from src.api.routes import router
from src.services.database import close_mongo_connection, connect_to_mongo

#helps intialize it + manage lifespan
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application startup and shutdown events."""
    await connect_to_mongo()
    yield

    await close_mongo_connection()

#creates a FastAPI instance
app = FastAPI(
    title=settings.app_name.title(),
    description="AI-native event production platform API",
    version="0.1.0",
    debug=settings.debug,
    lifespan=lifespan,
)

#allows cross-origin requests (front-end on another API to call)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.debug else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

#health status check
@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "healthy", "app": settings.app_name}

#direct execution
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
