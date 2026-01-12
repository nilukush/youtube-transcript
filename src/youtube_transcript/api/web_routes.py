"""Web UI routes for serving HTML templates.

This module contains the routes for serving the web UI with Jinja2 templates.
"""

import logging
from typing import Optional
from fastapi import APIRouter, Request, Response, Header
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import Session

from youtube_transcript.models import get_session
from youtube_transcript.services import TranscriptOrchestrator
from youtube_transcript.utils.url_parser import extract_video_id


logger = logging.getLogger(__name__)

# Create router for web UI routes
web_router = APIRouter(tags=["web-ui"])


@web_router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """
    Serve the index page with URL input form.

    Args:
        request: FastAPI Request object

    Returns:
        HTMLResponse with rendered index template
    """
    from fastapi.templating import Jinja2Templates

    templates = Jinja2Templates(directory="src/youtube_transcript/templates")
    return templates.TemplateResponse("index.html", {"request": request})


@web_router.get("/transcript", response_class=HTMLResponse)
async def get_transcript_web(
    request: Request,
    url: str,
    languages: Optional[str] = None,
):
    """
    Fetch and display transcript in web UI.

    Args:
        request: FastAPI Request object
        url: YouTube video URL
        languages: Optional comma-separated language codes

    Returns:
        HTMLResponse with rendered results or error template
    """
    from fastapi.templating import Jinja2Templates

    templates = Jinja2Templates(directory="src/youtube_transcript/templates")

    # Extract video ID
    video_id = extract_video_id(url)

    if not video_id:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error_title": "Invalid URL",
                "error_message": "Could not extract a valid video ID from the URL.",
                "show_help": True,
                "back_url": "/",
            }
        )

    # Fetch transcript
    session_gen = get_session()
    session = next(session_gen)

    # Create orchestrator (proxy auto-configured from environment variables)
    orchestrator = TranscriptOrchestrator(
        session=session
    )

    # Parse languages
    lang_list = None
    if languages:
        lang_list = [l.strip() for l in languages.split(",")]

    try:
        result = orchestrator.get_transcript(video_id, languages=lang_list)

        if not result:
            return templates.TemplateResponse(
                "error.html",
                {
                    "request": request,
                    "error_title": "Transcript Not Found",
                    "error_message": f"No transcript available for video '{video_id}'",
                    "error_details": "The video may not have a transcript, or it may be disabled.",
                    "show_help": True,
                    "back_url": "/",
                }
            )

        return templates.TemplateResponse(
            "results.html",
            {
                "request": request,
                "transcript": result,
                "error": None,
            }
        )
    except Exception as e:
        logger.error(f"Error fetching transcript for web UI: {e}")
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error_title": "Server Error",
                "error_message": "An error occurred while fetching the transcript.",
                "error_details": str(e),
                "show_help": True,
                "back_url": "/",
            }
        )


@web_router.get("/transcript/{video_id}", response_class=HTMLResponse)
async def get_transcript_by_id_web(
    request: Request,
    video_id: str,
    languages: Optional[str] = None,
):
    """
    Fetch and display transcript by video ID in web UI.

    Args:
        request: FastAPI Request object
        video_id: YouTube video ID
        languages: Optional comma-separated language codes

    Returns:
        HTMLResponse with rendered results or error template
    """
    from fastapi.templating import Jinja2Templates

    templates = Jinja2Templates(directory="src/youtube_transcript/templates")

    # Fetch transcript
    session_gen = get_session()
    session = next(session_gen)

    # Create orchestrator (proxy auto-configured from environment variables)
    orchestrator = TranscriptOrchestrator(
        session=session
    )

    # Parse languages
    lang_list = None
    if languages:
        lang_list = [l.strip() for l in languages.split(",")]

    try:
        result = orchestrator.get_transcript(video_id, languages=lang_list)

        if not result:
            return templates.TemplateResponse(
                "error.html",
                {
                    "request": request,
                    "error_title": "Transcript Not Found",
                    "error_message": f"No transcript available for video '{video_id}'",
                    "error_details": "The video may not have a transcript, or it may be disabled.",
                    "show_help": True,
                    "back_url": "/",
                }
            )

        return templates.TemplateResponse(
            "results.html",
            {
                "request": request,
                "transcript": result,
                "error": None,
            }
        )
    except Exception as e:
        logger.error(f"Error fetching transcript for web UI: {e}")
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error_title": "Server Error",
                "error_message": "An error occurred while fetching the transcript.",
                "error_details": str(e),
                "show_help": True,
                "back_url": "/",
            }
        )


@web_router.get("/htmx/transcript", response_class=HTMLResponse)
async def get_transcript_htmx(
    request: Request,
    url: str,
    languages: Optional[str] = None,
    hx_request: Optional[str] = Header(None, alias="HX-Request"),
):
    """
    Fetch transcript as HTML fragment for HTMX.

    This endpoint returns HTML fragments (not full pages) for HTMX to swap in.
    Used for dynamic content updates without page refresh.

    Args:
        request: FastAPI Request object
        url: YouTube video URL
        languages: Optional comma-separated language codes
        hx_request: HTMX request header (optional)

    Returns:
        HTMLResponse with transcript or error fragment
    """
    from fastapi.templating import Jinja2Templates

    templates = Jinja2Templates(directory="src/youtube_transcript/templates")

    # Extract video ID
    video_id = extract_video_id(url)

    if not video_id:
        # Return error fragment
        return templates.TemplateResponse(
            "partials/error_fragment.html",
            {
                "request": request,
                "error": "Could not extract a valid video ID from the URL.",
            },
        )

    # Fetch transcript
    session_gen = get_session()
    session = next(session_gen)

    # Create orchestrator (proxy auto-configured from environment variables)
    orchestrator = TranscriptOrchestrator(
        session=session
    )

    # Parse languages
    lang_list = None
    if languages:
        lang_list = [l.strip() for l in languages.split(",")]

    try:
        result = orchestrator.get_transcript(video_id, languages=lang_list)

        if not result:
            # Return error fragment
            return templates.TemplateResponse(
                "partials/error_fragment.html",
                {
                    "request": request,
                    "error": f"No transcript available for video '{video_id}'",
                },
            )

        # Return transcript fragment
        return templates.TemplateResponse(
            "partials/transcript_fragment.html",
            {
                "request": request,
                "transcript": result,
            },
        )
    except Exception as e:
        logger.error(f"Error fetching transcript for HTMX: {e}")
        # Return error fragment
        return templates.TemplateResponse(
            "partials/error_fragment.html",
            {
                "request": request,
                "error": f"An error occurred: {str(e)}",
            },
        )
