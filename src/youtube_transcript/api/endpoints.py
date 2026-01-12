"""Transcript API endpoints.

This module contains the REST API endpoints for transcript retrieval.
Each endpoint uses dependency injection to access the TranscriptOrchestrator.
"""

import logging
from typing import Optional, List
from fastapi import APIRouter, HTTPException, status, Query, Depends

from youtube_transcript.api.models import TranscriptRequest, TranscriptResponse, ErrorResponse
from youtube_transcript.services.fetcher import TranscriptResult
from youtube_transcript.services import TranscriptOrchestrator
from youtube_transcript.utils.url_parser import extract_video_id


logger = logging.getLogger(__name__)

# Create router for transcript endpoints
router = APIRouter(tags=["transcript"])


def get_orchestrator():
    """
    Dependency injection for TranscriptOrchestrator.

    This function provides a fresh orchestrator instance for each request.

    Returns:
        TranscriptOrchestrator: Service orchestrator instance
    """
    from sqlmodel import Session
    from youtube_transcript.models import get_session
    from youtube_transcript.services import TranscriptOrchestrator

    session_gen = get_session()
    session = next(session_gen)
    return TranscriptOrchestrator(session=session)


@router.post("/api/transcript", response_model=TranscriptResponse, status_code=status.HTTP_200_OK)
async def fetch_transcript_by_url(
    request: TranscriptRequest,
    orchestrator: TranscriptOrchestrator = Depends(get_orchestrator),
) -> TranscriptResponse:
    """
    Fetch transcript by YouTube URL.

    This endpoint accepts a YouTube URL in any supported format (watch, youtu.be,
    shorts, live, embed, etc.) and returns the transcript if available.

    The retrieval strategy is:
    1. Check Redis cache (fastest)
    2. Check database (fast)
    3. Fetch from YouTube API (slowest, populate cache and database)

    Args:
        request: TranscriptRequest with url and optional languages
        orchestrator: Injected TranscriptOrchestrator service

    Returns:
        TranscriptResponse with video_id, transcript, language, and type

    Raises:
        HTTPException 404: If transcript not found
        HTTPException 500: If service error occurs
    """
    try:
        # Extract video ID from URL
        video_id = extract_video_id(request.url)

        if not video_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Could not extract valid video ID from URL"
            )

        logger.info(f"Fetching transcript for video '{video_id}' from URL: {request.url}")

        # Fetch transcript using orchestrator
        result: Optional[TranscriptResult] = orchestrator.get_transcript(
            video_id,
            languages=request.languages
        )

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Transcript not found for video '{video_id}'"
            )

        # Convert to response model
        return TranscriptResponse.from_transcript_result(result)

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Error fetching transcript by URL: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch transcript: {str(e)}"
        )


@router.get("/api/transcript/{video_id}", response_model=TranscriptResponse, status_code=status.HTTP_200_OK)
async def fetch_transcript_by_video_id(
    video_id: str,
    languages: Optional[List[str]] = Query(default=None, description="Preferred language codes"),
    orchestrator: TranscriptOrchestrator = Depends(get_orchestrator),
) -> TranscriptResponse:
    """
    Fetch transcript by video ID.

    This endpoint accepts a YouTube video ID directly and returns the transcript
    if available. This is useful when you already have the video ID and don't
    need URL parsing.

    The retrieval strategy is:
    1. Check Redis cache (fastest)
    2. Check database (fast)
    3. Fetch from YouTube API (slowest, populate cache and database)

    Args:
        video_id: YouTube video ID (11 characters typically)
        languages: Optional list of preferred language codes
        orchestrator: Injected TranscriptOrchestrator service

    Returns:
        TranscriptResponse with video_id, transcript, language, and type

    Raises:
        HTTPException 404: If transcript not found
        HTTPException 500: If service error occurs
    """
    try:
        logger.info(f"Fetching transcript for video ID: '{video_id}'")

        # Fetch transcript using orchestrator
        result: Optional[TranscriptResult] = orchestrator.get_transcript(
            video_id,
            languages=languages
        )

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Transcript not found for video '{video_id}'"
            )

        # Convert to response model
        return TranscriptResponse.from_transcript_result(result)

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Error fetching transcript by video ID: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch transcript: {str(e)}"
        )
