"""Pydantic models for API request and response validation."""

from typing import Optional
from pydantic import BaseModel, Field, HttpUrl, validator

from youtube_transcript.services.fetcher import TranscriptResult


class TranscriptRequest(BaseModel):
    """
    Request model for fetching a transcript.

    Attributes:
        url: YouTube video URL (any supported format)
        languages: Optional list of preferred language codes
    """

    url: str = Field(..., description="YouTube video URL")
    languages: Optional[list[str]] = Field(
        default=None,
        description="Optional list of preferred language codes (e.g., ['en', 'es'])"
    )

    @validator('url')
    def validate_url(cls, v):
        """Validate that URL is not empty and looks like a URL."""
        if not v or not isinstance(v, str):
            raise ValueError('URL must be a non-empty string')

        # Basic validation - should contain http or https
        v = v.strip()
        if not v.startswith(('http://', 'https://')):
            # Try to add https for convenience
            if v.startswith(('www.', 'youtu.be', 'youtube.com')):
                v = 'https://' + v
            else:
                raise ValueError('URL must start with http:// or https://')

        return v

    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "languages": ["en", "es"]
            }
        }


class TranscriptResponse(BaseModel):
    """
    Response model for transcript data.

    Attributes:
        video_id: YouTube video ID
        transcript: Full transcript text
        language: Language code of the transcript
        transcript_type: Type of transcript (manual or auto)
    """

    video_id: str = Field(..., description="YouTube video ID", min_length=1, max_length=20)
    transcript: str = Field(..., description="Full transcript text")
    language: str = Field(..., description="Language code (e.g., 'en', 'es')", max_length=10)
    transcript_type: str = Field(
        ...,
        description="Type of transcript: 'manual' or 'auto'",
        pattern='^(manual|auto)$'
    )

    @classmethod
    def from_transcript_result(cls, result: TranscriptResult) -> 'TranscriptResponse':
        """
        Create TranscriptResponse from TranscriptResult.

        Args:
            result: TranscriptResult from service layer

        Returns:
            TranscriptResponse instance
        """
        return cls(
            video_id=result.video_id,
            transcript=result.transcript,
            language=result.language,
            transcript_type=result.transcript_type,
        )

    class Config:
        json_schema_extra = {
            "example": {
                "video_id": "dQw4w9WgXcQ",
                "transcript": "Never gonna give you up...",
                "language": "en",
                "transcript_type": "manual"
            }
        }


class ErrorResponse(BaseModel):
    """
    Standard error response model.

    Attributes:
        error: Error type or message
        detail: Detailed error description
    """

    error: str = Field(..., description="Error type or message")
    detail: Optional[str] = Field(default=None, description="Detailed error description")

    class Config:
        json_schema_extra = {
            "example": {
                "error": "Not Found",
                "detail": "Transcript not found for this video"
            }
        }
