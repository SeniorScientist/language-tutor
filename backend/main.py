"""FastAPI application for Foreign Language Tutor."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from models import HealthResponse
from routers import chat_router, correction_router, exercises_router, training_router
from providers import get_llm_provider
from services import get_rag_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    logger.info("Starting Foreign Language Tutor API...")
    settings = get_settings()
    logger.info(f"LLM Provider: {settings.llm_provider}")

    # Initialize services (warm up)
    try:
        logger.info("Initializing RAG service...")
        get_rag_service()
        logger.info("RAG service initialized")
    except Exception as e:
        logger.error(f"Failed to initialize RAG service: {e}")

    try:
        logger.info("Initializing LLM provider...")
        get_llm_provider()
        logger.info("LLM provider initialized")
    except Exception as e:
        logger.error(f"Failed to initialize LLM provider: {e}")

    logger.info("Application started successfully")

    yield

    # Shutdown
    logger.info("Shutting down Foreign Language Tutor API...")


# Create FastAPI app
app = FastAPI(
    title="Foreign Language Tutor API",
    description="AI-powered language tutoring with chat, grammar correction, and exercises",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
settings = get_settings()
logger.info(f"CORS origins: {settings.cors_origins}")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include routers
app.include_router(chat_router)
app.include_router(correction_router)
app.include_router(exercises_router)
app.include_router(training_router)


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Check the health status of all services."""
    settings = get_settings()

    # Check LLM provider
    llm_status = "unknown"
    try:
        provider = get_llm_provider()
        is_healthy = await provider.health_check()
        llm_status = "healthy" if is_healthy else "unhealthy"
    except Exception as e:
        logger.error(f"LLM health check error: {e}")
        llm_status = f"error: {str(e)}"

    # Check RAG service
    rag_status = "unknown"
    try:
        rag = get_rag_service()
        is_healthy = rag.health_check()
        rag_status = "healthy" if is_healthy else "unhealthy"
    except Exception as e:
        logger.error(f"RAG health check error: {e}")
        rag_status = f"error: {str(e)}"

    return HealthResponse(
        status="ok",
        llm_provider=settings.llm_provider,
        llm_status=llm_status,
        rag_status=rag_status,
    )


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Foreign Language Tutor API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
