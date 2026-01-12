"""FastAPI application factory."""

from typing import Optional
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session

from youtube_transcript.models import get_session, init_db
from youtube_transcript.services import TranscriptOrchestrator


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events."""
    # Startup
    init_db()
    yield
    # Shutdown
    # Add cleanup code here if needed


def create_app(
    cors_origins: Optional[list[str]] = None,
) -> FastAPI:
    """
    Create and configure the FastAPI application.

    Args:
        cors_origins: List of allowed CORS origins

    Returns:
        Configured FastAPI application
    """
    if cors_origins is None:
        cors_origins = [
            "http://localhost",
            "http://localhost:8000",
            "http://localhost:3000",
            "http://127.0.0.1",
            "http://127.0.0.1:8000",
        ]

    app = FastAPI(
        title="YouTube Transcript Fetcher API",
        description="API for fetching YouTube video transcripts with caching",
        version="0.1.0",
        lifespan=lifespan,
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Mount static files
    static_dir = Path(__file__).parent.parent / "static"
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    # Include routers
    from youtube_transcript.api.endpoints import router as transcript_router
    from youtube_transcript.api.web_routes import web_router

    # Web UI routes (must be before API routes to avoid conflicts)
    app.include_router(web_router)

    # API routes
    app.include_router(transcript_router)

    # Add health check endpoints
    @app.get("/health")
    async def health():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "service": "youtube-transcript-fetcher",
            "version": app.version,
        }

    # Exception handlers
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """Handle HTTP exceptions."""
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.detail, "status_code": exc.status_code}
        )

    return app


# Create the default app instance
app = create_app()


# Dependency injection
def get_orchestrator() -> TranscriptOrchestrator:
    """
    Get orchestrator instance (dependency injection).

    This will be enhanced in Step 10 with proper session management.
    """
    # TODO: Proper dependency injection with session
    from youtube_transcript.models import get_session

    session_gen = get_session()
    session = next(session_gen)
    return TranscriptOrchestrator(session=session)
