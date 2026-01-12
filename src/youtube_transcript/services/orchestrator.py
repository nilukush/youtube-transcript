"""Transcript service orchestrator."""

import logging
from typing import Optional
import redis
from sqlmodel import Session

from youtube_transcript.services.fetcher import (
    YouTubeTranscriptFetcher,
    TranscriptResult,
)
from youtube_transcript.services.cache import TranscriptCache
from youtube_transcript.services.repository import TranscriptRepository


logger = logging.getLogger(__name__)


class TranscriptOrchestrator:
    """
    Orchestrator for transcript services.

    This service coordinates between the fetcher, cache, and repository
    to provide a unified API for transcript retrieval with intelligent
    fallback and caching strategies.

    Retrieval Strategy:
    1. Check Redis cache (fastest)
    2. Check database (fast)
    3. Fetch from YouTube API (slowest, populate cache and database)

    Attributes:
        fetcher: YouTubeTranscriptFetcher instance
        cache: TranscriptCache instance
        repository: TranscriptRepository instance

    Example:
        >>> from youtube_transcript.models import get_session
        >>>
        >>> session_gen = get_session()
        >>> session = next(session_gen)
        >>>
        >>> orchestrator = TranscriptOrchestrator(session=session)
        >>> result = orchestrator.get_transcript('dQw4w9WgXcQ')
        >>> print(result.transcript)
    """

    def __init__(
        self,
        session: Session,
        cache: Optional[TranscriptCache] = None,
        fetcher: Optional[YouTubeTranscriptFetcher] = None,
        proxy_config=None,
    ):
        """
        Initialize the orchestrator with all required services.

        Args:
            session: SQLModel Session for database operations
            cache: Optional TranscriptCache instance (creates default if None)
            fetcher: Optional fetcher instance (creates default if None)
            proxy_config: Optional proxy configuration for YouTube API requests

        Example:
            >>> from youtube_transcript.config import get_proxy_config
            >>>
            >>> # With proxy from environment
            >>> orchestrator = TranscriptOrchestrator(
            ...     session=session,
            ...     proxy_config=get_proxy_config()
            ... )
        """
        self.session = session

        # Create fetcher with proxy config if provided and no custom fetcher given
        if fetcher is None:
            from youtube_transcript.config import get_proxy_config
            # Use provided proxy_config or load from environment
            config = proxy_config or get_proxy_config()
            self.fetcher = YouTubeTranscriptFetcher(proxy_config=config)
        else:
            self.fetcher = fetcher

        self.cache = cache or TranscriptCache()
        self.repository = TranscriptRepository(session)

    def get_transcript(
        self,
        video_id: str,
        languages: Optional[list[str]] = None,
    ) -> Optional[TranscriptResult]:
        """
        Get a transcript using intelligent fallback strategy.

        Strategy:
        1. Check Redis cache
        2. Check database
        3. Fetch from YouTube API

        Args:
            video_id: YouTube video ID
            languages: Optional list of language codes to try

        Returns:
            TranscriptResult if found, None otherwise
        """
        # Step 1: Try cache first (fastest)
        try:
            cached = self.cache.get(video_id)
            if cached:
                logger.debug(f"Cache hit for video '{video_id}'")
                return cached
        except Exception as e:
            logger.warning(f"Cache lookup failed for '{video_id}': {e}")

        # Step 2: Try database (fast)
        try:
            db_transcript = self.repository.get_by_video_id(video_id)
            if db_transcript:
                logger.debug(f"Database hit for video '{video_id}'")
                result = self.repository._to_transcript_result(db_transcript)
                # Populate cache for next time
                try:
                    self.cache.set(video_id, result)
                except Exception as e:
                    logger.warning(f"Failed to cache transcript for '{video_id}': {e}")
                return result
        except Exception as e:
            logger.warning(f"Database lookup failed for '{video_id}': {e}")

        # Step 3: Fetch from API (slowest)
        try:
            logger.debug(f"Fetching from API for video '{video_id}'")
            result = self.fetcher.fetch_transcript(video_id, languages=languages)
            if result:
                # Populate cache
                try:
                    self.cache.set(video_id, result)
                except Exception as e:
                    logger.warning(f"Failed to cache transcript for '{video_id}': {e}")

                # Populate database
                try:
                    self.repository.upsert(result)
                except Exception as e:
                    logger.warning(f"Failed to save transcript to database for '{video_id}': {e}")

                return result
        except Exception as e:
            logger.error(f"Failed to fetch transcript for '{video_id}': {e}")

        # Not found anywhere
        return None

    def invalidate_cache(self, video_id: str) -> bool:
        """
        Invalidate cached transcript for a video.

        Args:
            video_id: YouTube video ID

        Returns:
            True if invalidated, False if not cached
        """
        try:
            return self.cache.delete(video_id)
        except Exception as e:
            logger.error(f"Failed to invalidate cache for '{video_id}': {e}")
            return False

    def clear_cache(self) -> bool:
        """
        Clear all cached transcripts.

        Returns:
            True if successful, False otherwise
        """
        try:
            return self.cache.clear_all()
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
            return False

    def prefetch(self, video_id: str) -> Optional[TranscriptResult]:
        """
        Prefetch a transcript (fetch and cache regardless of current state).

        This is useful for warming up the cache with expected transcripts.

        Args:
            video_id: YouTube video ID

        Returns:
            TranscriptResult if found, None otherwise
        """
        try:
            result = self.fetcher.fetch_transcript(video_id)
            if result:
                # Populate cache
                self.cache.set(video_id, result)
                # Populate database
                self.repository.upsert(result)
                return result
        except Exception as e:
            logger.error(f"Failed to prefetch transcript for '{video_id}': {e}")

        return None

    def get_statistics(self) -> dict:
        """
        Get statistics about cache and database.

        Returns:
            Dictionary with statistics
        """
        try:
            cache_stats = self.cache.get_stats()
            db_count = self.repository.count()

            return {
                'cache_keys': cache_stats.get('total_keys', 0),
                'cache_memory': cache_stats.get('memory_human', '0B'),
                'database_count': db_count,
            }
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {
                'cache_keys': 0,
                'cache_memory': '0B',
                'database_count': 0,
            }
