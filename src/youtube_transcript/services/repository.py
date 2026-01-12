"""Transcript database repository service."""

import logging
from typing import Optional, List
from sqlmodel import Session, select

from youtube_transcript.models import Transcript
from youtube_transcript.services.fetcher import TranscriptResult


logger = logging.getLogger(__name__)


class TranscriptRepository:
    """
    Repository for transcript database operations.

    This service provides CRUD operations for Transcript model,
    with automatic conversion between Transcript and TranscriptResult.

    Attributes:
        session: SQLModel database session

    Example:
        >>> from youtube_transcript.models import get_session
        >>> from youtube_transcript.services import TranscriptRepository
        >>>
        >>> session_gen = get_session()
        >>> session = next(session_gen)
        >>> repository = TranscriptRepository(session)
        >>>
        >>> result = TranscriptResult(...)
        >>> transcript = repository.create(result)
    """

    def __init__(self, session: Session):
        """
        Initialize the repository with a database session.

        Args:
            session: SQLModel Session for database operations
        """
        self.session = session

    def create(self, result: TranscriptResult) -> Optional[Transcript]:
        """
        Create a new transcript in the database.

        Args:
            result: TranscriptResult to save

        Returns:
            Created Transcript model or None if creation failed
        """
        try:
            transcript = self._to_transcript(result)
            self.session.add(transcript)
            self.session.commit()
            self.session.refresh(transcript)
            return transcript

        except Exception as e:
            logger.error(f"Failed to create transcript for video '{result.video_id}': {e}")
            self.session.rollback()
            return None

    def get_by_id(self, transcript_id: int) -> Optional[Transcript]:
        """
        Retrieve a transcript by its primary key ID.

        Args:
            transcript_id: Primary key ID

        Returns:
            Transcript if found, None otherwise
        """
        try:
            statement = select(Transcript).where(Transcript.id == transcript_id)
            return self.session.exec(statement).first()

        except Exception as e:
            logger.error(f"Failed to retrieve transcript by ID '{transcript_id}': {e}")
            return None

    def get_by_video_id(self, video_id: str) -> Optional[Transcript]:
        """
        Retrieve a transcript by YouTube video ID.

        Args:
            video_id: YouTube video ID

        Returns:
            Transcript if found, None otherwise
        """
        try:
            statement = select(Transcript).where(Transcript.video_id == video_id)
            return self.session.exec(statement).first()

        except Exception as e:
            logger.error(f"Failed to retrieve transcript for video '{video_id}': {e}")
            return None

    def update(self, transcript_id: int, result: TranscriptResult) -> Optional[Transcript]:
        """
        Update an existing transcript.

        Args:
            transcript_id: Primary key ID of transcript to update
            result: New TranscriptResult data

        Returns:
            Updated Transcript or None if not found
        """
        try:
            transcript = self.get_by_id(transcript_id)
            if not transcript:
                return None

            # Update fields
            transcript.transcript_text = result.transcript
            transcript.language = result.language
            transcript.transcript_type = result.transcript_type
            # Manually update the timestamp
            from datetime import datetime, timezone
            transcript.updated_at = datetime.now(timezone.utc)

            self.session.commit()
            self.session.refresh(transcript)
            return transcript

        except Exception as e:
            logger.error(f"Failed to update transcript '{transcript_id}': {e}")
            self.session.rollback()
            return None

    def upsert(self, result: TranscriptResult) -> Optional[Transcript]:
        """
        Create or update a transcript (upsert operation).

        If a transcript with the same video_id exists, it will be updated.
        Otherwise, a new transcript will be created.

        Args:
            result: TranscriptResult to upsert

        Returns:
            Created or updated Transcript
        """
        try:
            # Check if transcript exists
            existing = self.get_by_video_id(result.video_id)

            if existing:
                # Update existing
                existing.transcript_text = result.transcript
                existing.language = result.language
                existing.transcript_type = result.transcript_type
                # Manually update the timestamp
                from datetime import datetime, timezone
                existing.updated_at = datetime.now(timezone.utc)
                self.session.commit()
                self.session.refresh(existing)
                return existing
            else:
                # Create new
                return self.create(result)

        except Exception as e:
            logger.error(f"Failed to upsert transcript for video '{result.video_id}': {e}")
            self.session.rollback()
            return None

    def delete(self, transcript_id: int) -> bool:
        """
        Delete a transcript by ID.

        Args:
            transcript_id: Primary key ID of transcript to delete

        Returns:
            True if deleted, False if not found
        """
        try:
            transcript = self.get_by_id(transcript_id)
            if not transcript:
                return False

            self.session.delete(transcript)
            self.session.commit()
            return True

        except Exception as e:
            logger.error(f"Failed to delete transcript '{transcript_id}': {e}")
            self.session.rollback()
            return False

    def delete_by_video_id(self, video_id: str) -> bool:
        """
        Delete a transcript by video ID.

        Args:
            video_id: YouTube video ID

        Returns:
            True if deleted, False if not found
        """
        try:
            transcript = self.get_by_video_id(video_id)
            if not transcript:
                return False

            self.session.delete(transcript)
            self.session.commit()
            return True

        except Exception as e:
            logger.error(f"Failed to delete transcript for video '{video_id}': {e}")
            self.session.rollback()
            return False

    def exists_by_video_id(self, video_id: str) -> bool:
        """
        Check if a transcript exists for a video ID.

        Args:
            video_id: YouTube video ID

        Returns:
            True if exists, False otherwise
        """
        try:
            statement = select(Transcript).where(Transcript.video_id == video_id)
            result = self.session.exec(statement).first()
            return result is not None

        except Exception as e:
            logger.error(f"Failed to check existence for video '{video_id}': {e}")
            return False

    def all(self) -> List[Transcript]:
        """
        Get all transcripts in the database.

        Returns:
            List of all Transcript models
        """
        try:
            statement = select(Transcript)
            results = self.session.exec(statement).all()
            return list(results)

        except Exception as e:
            logger.error(f"Failed to retrieve all transcripts: {e}")
            return []

    def list_with_limit(self, limit: int) -> List[Transcript]:
        """
        Get a limited number of transcripts.

        Args:
            limit: Maximum number of transcripts to return

        Returns:
            List of Transcript models
        """
        try:
            statement = select(Transcript).limit(limit)
            results = self.session.exec(statement).all()
            return list(results)

        except Exception as e:
            logger.error(f"Failed to retrieve transcripts with limit: {e}")
            return []

    def list_by_language(self, language: str) -> List[Transcript]:
        """
        Get all transcripts for a specific language.

        Args:
            language: Language code (e.g., 'en', 'es')

        Returns:
            List of Transcript models
        """
        try:
            statement = select(Transcript).where(Transcript.language == language)
            results = self.session.exec(statement).all()
            return list(results)

        except Exception as e:
            logger.error(f"Failed to retrieve transcripts for language '{language}': {e}")
            return []

    def count(self) -> int:
        """
        Get the total number of transcripts in the database.

        Returns:
            Count of transcripts
        """
        try:
            statement = select(Transcript)
            results = self.session.exec(statement).all()
            return len(results)

        except Exception as e:
            logger.error(f"Failed to count transcripts: {e}")
            return 0

    def _to_transcript(self, result: TranscriptResult) -> Transcript:
        """
        Convert a TranscriptResult to a Transcript model.

        Args:
            result: TranscriptResult to convert

        Returns:
            Transcript model
        """
        return Transcript(
            video_id=result.video_id,
            transcript_text=result.transcript,
            language=result.language,
            transcript_type=result.transcript_type,
        )

    def _to_transcript_result(self, transcript: Transcript) -> TranscriptResult:
        """
        Convert a Transcript model to a TranscriptResult.

        Args:
            transcript: Transcript model to convert

        Returns:
            TranscriptResult
        """
        return TranscriptResult(
            video_id=transcript.video_id,
            transcript=transcript.transcript_text,
            language=transcript.language,
            transcript_type=transcript.transcript_type,
            duration=0.0,  # Duration not stored in database
        )
