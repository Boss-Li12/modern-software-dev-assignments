# ============================================================
# TODO 3: Refactored Main Application (AI-Generated)
# ============================================================
"""
FastAPI application entry point with proper lifecycle management,
configuration, and error handling.

AI-Generated: This file was refactored with AI assistance for TODO 3.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .config import settings
from .db import init_db
from .exceptions import AppException
from .routers import action_items, notes
from .schemas import ErrorResponse


# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# ============================================================
# Application Lifecycle
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifecycle manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Debug mode: {settings.debug}")
    
    # Initialize database
    try:
        init_db()
        logger.info(f"Database initialized at {settings.db_path}")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
    
    yield  # Application runs here
    
    # Shutdown
    logger.info("Shutting down application")


# ============================================================
# Application Factory
# ============================================================

def create_app() -> FastAPI:
    """
    Application factory function.
    Creates and configures the FastAPI application.
    """
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Extract action items from free-form notes using heuristics or LLM",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )
    
    # Register exception handlers
    register_exception_handlers(app)
    
    # Register routers
    app.include_router(notes.router)
    app.include_router(action_items.router)
    
    # Mount static files
    static_dir = Path(__file__).resolve().parents[1] / "frontend"
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    
    # Register root endpoint
    @app.get("/", response_class=HTMLResponse, include_in_schema=False)
    def index() -> str:
        """Serve the frontend HTML page."""
        html_path = Path(__file__).resolve().parents[1] / "frontend" / "index.html"
        if html_path.exists():
            return html_path.read_text(encoding="utf-8")
        return "<html><body><h1>Action Item Extractor</h1><p>Frontend not found.</p></body></html>"
    
    # Health check endpoint
    @app.get("/health", tags=["health"])
    def health_check() -> dict:
        """Health check endpoint for monitoring."""
        return {
            "status": "healthy",
            "app": settings.app_name,
            "version": settings.app_version
        }
    
    return app


# ============================================================
# Exception Handlers
# ============================================================

def register_exception_handlers(app: FastAPI) -> None:
    """Register custom exception handlers."""
    
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        """Handle application-specific exceptions."""
        logger.warning(f"AppException: {exc.error_type} - {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                error=exc.error_type,
                detail=exc.detail,
                status_code=exc.status_code
            ).model_dump()
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Handle unexpected exceptions."""
        logger.error(f"Unexpected error: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                error="internal_error",
                detail="An unexpected error occurred",
                status_code=500
            ).model_dump()
        )


# ============================================================
# Application Instance
# ============================================================

# Create the application instance
app = create_app()