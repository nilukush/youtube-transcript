"""Redis transcript cache service."""

import json
import logging
from typing import Optional
import redis

from youtube_transcript.services.fetcher import TranscriptResult


logger = logging.getLogger(__name__)


class TranscriptCache:
    """
    Redis-based cache for YouTube transcripts.

    This service provides caching for TranscriptResult objects using Redis.
    It reduces API calls to YouTube by storing fetched transcripts in memory
    with configurable TTL.

    Attributes:
        redis_client: Redis client instance
        ttl: Time-to-live for cache entries in seconds (default: 7 days)
        prefix: Prefix for all cache keys (default: 'ytt')

    Example:
        >>> cache = TranscriptCache()
        >>> result = TranscriptResult(video_id='abc', transcript='Hello', ...)
        >>> cache.set('abc', result)
        >>> cached = cache.get('abc')
        >>> print(cached.transcript)
        'Hello'
    """

    DEFAULT_TTL = 604800  # 7 days in seconds
    DEFAULT_PREFIX = "ytt"

    def __init__(
        self,
        redis_client: Optional[redis.Redis] = None,
        ttl: int = DEFAULT_TTL,
        prefix: str = DEFAULT_PREFIX,
    ):
        """
        Initialize the transcript cache.

        Args:
            redis_client: Optional Redis client (creates new one if None)
            ttl: Time-to-live for cache entries in seconds
            prefix: Prefix for cache keys
        """
        if redis_client is None:
            # Create default Redis client
            # In production, these should come from environment variables
            redis_client = redis.Redis(
                host='localhost',
                port=6379,
                db=0,
                decode_responses=False,  # Return bytes, we'll decode manually
            )

        self.redis_client = redis_client
        self.ttl = ttl
        self.prefix = prefix

    def _generate_key(self, video_id: str) -> str:
        """
        Generate a cache key for a video ID.

        Args:
            video_id: YouTube video ID

        Returns:
            Cache key string
        """
        return f"{self.prefix}:transcript:{video_id}"

    def set(self, video_id: str, result: TranscriptResult) -> bool:
        """
        Store a transcript in the cache.

        Args:
            video_id: YouTube video ID
            result: TranscriptResult to cache

        Returns:
            True if successful, False otherwise
        """
        try:
            key = self._generate_key(video_id)

            # Serialize TranscriptResult to JSON
            data = {
                'video_id': result.video_id,
                'transcript': result.transcript,
                'language': result.language,
                'transcript_type': result.transcript_type,
                'duration': result.duration,
            }

            json_data = json.dumps(data)

            # Store in Redis
            self.redis_client.set(key, json_data.encode('utf-8'))

            # Set TTL
            self.redis_client.expire(key, self.ttl)

            return True

        except Exception as e:
            logger.error(f"Failed to cache transcript for video '{video_id}': {e}")
            return False

    def get(self, video_id: str) -> Optional[TranscriptResult]:
        """
        Retrieve a transcript from the cache.

        Args:
            video_id: YouTube video ID

        Returns:
            TranscriptResult if found, None otherwise
        """
        try:
            key = self._generate_key(video_id)

            # Get from Redis
            data = self.redis_client.get(key)

            if data is None:
                return None

            # Decode and deserialize
            json_data = data.decode('utf-8')
            parsed = json.loads(json_data)

            # Create TranscriptResult from parsed data
            return TranscriptResult(
                video_id=parsed['video_id'],
                transcript=parsed['transcript'],
                language=parsed.get('language', 'en'),
                transcript_type=parsed.get('transcript_type', 'auto'),
                duration=parsed.get('duration', 0.0),
            )

        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode cached transcript for '{video_id}': {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to retrieve transcript for '{video_id}': {e}")
            return None

    def delete(self, video_id: str) -> bool:
        """
        Delete a transcript from the cache.

        Args:
            video_id: YouTube video ID

        Returns:
            True if deleted, False if not found or error
        """
        try:
            key = self._generate_key(video_id)
            result = self.redis_client.delete(key)
            return result > 0

        except Exception as e:
            logger.error(f"Failed to delete transcript for '{video_id}': {e}")
            return False

    def exists(self, video_id: str) -> bool:
        """
        Check if a transcript is in the cache.

        Args:
            video_id: YouTube video ID

        Returns:
            True if cached, False otherwise
        """
        try:
            key = self._generate_key(video_id)
            result = self.redis_client.exists(key)
            return result > 0

        except Exception as e:
            logger.error(f"Failed to check cache for '{video_id}': {e}")
            return False

    def clear_all(self) -> bool:
        """
        Clear all cached transcripts.

        Returns:
            True if successful, False otherwise
        """
        try:
            pattern = f"{self.prefix}:transcript:*"
            keys = self.redis_client.keys(pattern)

            if keys:
                self.redis_client.delete(*keys)

            return True

        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
            return False

    def get_ttl(self, video_id: str) -> int:
        """
        Get remaining TTL for a cached transcript.

        Args:
            video_id: YouTube video ID

        Returns:
            Remaining TTL in seconds, -2 if key doesn't exist, -1 if no expiry
        """
        try:
            key = self._generate_key(video_id)
            return self.redis_client.ttl(key)

        except Exception as e:
            logger.error(f"Failed to get TTL for '{video_id}': {e}")
            return -2

    def get_stats(self) -> dict:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        try:
            db_size = self.redis_client.dbsize()
            info = self.redis_client.info()

            return {
                'total_keys': db_size,
                'memory_used': info.get('used_memory', 0),
                'memory_human': info.get('used_memory_human', '0B'),
            }

        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {
                'total_keys': 0,
                'memory_used': 0,
                'memory_human': '0B',
            }
