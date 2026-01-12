"""Transcript database model."""

from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Field, SQLModel


class Transcript(SQLModel, table=True):
    """
    YouTube video transcript model.

    Represents a fetched transcript from a YouTube video, stored in the database
    for caching and persistence.

    Attributes:
        id: Primary key
        video_id: YouTube video ID (unique, indexed)
        transcript_text: Full transcript text content
        language: Transcript language code (default: "en")
        transcript_type: Type of transcript ("manual" or "auto")
        created_at: Timestamp when transcript was first created
        updated_at: Timestamp when transcript was last updated
        cache_key: Optional cache key for Redis lookup
    """

    __tablename__ = "transcripts"

    id: Optional[int] = Field(default=None, primary_key=True)
    video_id: str = Field(index=True, unique=True, max_length=20)
    transcript_text: str = Field(default="")
    language: str = Field(default="en", max_length=10)
    transcript_type: str = Field(default="auto", max_length=10)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    cache_key: Optional[str] = Field(default=None, max_length=100)

    def __repr__(self) -> str:
        """Return string representation of Transcript."""
        return f"Transcript(id={self.id}, video_id='{self.video_id}', language='{self.language}')"

    def __str__(self) -> str:
        """Return user-friendly string representation."""
        return f"Transcript for video {self.video_id} ({self.language})"
