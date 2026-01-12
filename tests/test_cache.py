"""
Test Redis transcript cache.

These tests verify that TranscriptCache can cache and retrieve transcripts using Redis.
Following TDD: Write tests first, watch them fail, then implement to pass.
"""

import json
import time
from unittest.mock import Mock, patch
import pytest

from youtube_transcript.services.fetcher import TranscriptResult
from youtube_transcript.services.cache import TranscriptCache


class TestTranscriptCacheCreation:
    """Test cache instantiation and initialization."""

    @patch('youtube_transcript.services.cache.redis.Redis')
    def test_cache_can_be_created_with_default_settings(self, mock_redis):
        """Test that TranscriptCache can be instantiated with default settings."""
        mock_redis.return_value = Mock()

        cache = TranscriptCache()
        assert cache is not None
        assert cache.ttl == 604800  # 7 days in seconds

    @patch('youtube_transcript.services.cache.redis.Redis')
    def test_cache_can_be_created_with_custom_ttl(self, mock_redis):
        """Test that TranscriptCache can be instantiated with custom TTL."""
        mock_redis.return_value = Mock()

        cache = TranscriptCache(ttl=3600)  # 1 hour
        assert cache is not None
        assert cache.ttl == 3600


class TestCacheKeyGeneration:
    """Test cache key generation for video IDs."""

    @patch('youtube_transcript.services.cache.redis.Redis')
    def test_generate_cache_key_for_video_id(self, mock_redis):
        """Test cache key generation for a simple video ID."""
        mock_redis.return_value = Mock()

        cache = TranscriptCache()
        key = cache._generate_key('dQw4w9WgXcQ')

        assert key == 'ytt:transcript:dQw4w9WgXcQ'

    @patch('youtube_transcript.services.cache.redis.Redis')
    def test_generate_cache_key_with_custom_prefix(self, mock_redis):
        """Test cache key generation with custom prefix."""
        mock_redis.return_value = Mock()

        cache = TranscriptCache(prefix='custom')
        key = cache._generate_key('test123')

        assert key == 'custom:transcript:test123'

    @patch('youtube_transcript.services.cache.redis.Redis')
    def test_generate_cache_key_handles_special_characters(self, mock_redis):
        """Test that cache keys handle special characters in video IDs."""
        mock_redis.return_value = Mock()

        cache = TranscriptCache()
        # Video IDs shouldn't have special chars, but test robustness
        key = cache._generate_key('test-123')

        assert 'test-123' in key


class TestCacheSetOperations:
    """Test cache set operations."""

    @patch('youtube_transcript.services.cache.redis.Redis')
    def test_set_stores_transcript_in_cache(self, mock_redis):
        """Test that set() stores a transcript in Redis."""
        mock_redis_client = Mock()
        mock_redis.return_value = mock_redis_client

        cache = TranscriptCache()
        result = TranscriptResult(
            video_id='test123',
            transcript='Sample transcript text',
            language='en',
            transcript_type='manual',
            duration=120.5,
        )

        cache.set('test123', result)

        # Verify Redis set was called
        mock_redis_client.set.assert_called_once()
        call_args = mock_redis_client.set.call_args
        assert 'test123' in str(call_args)

    @patch('youtube_transcript.services.cache.redis.Redis')
    def test_set_serializes_transcript_result_to_json(self, mock_redis):
        """Test that TranscriptResult is properly serialized to JSON."""
        mock_redis_client = Mock()
        mock_redis.return_value = mock_redis_client

        cache = TranscriptCache()
        result = TranscriptResult(
            video_id='abc123',
            transcript='Hello world',
            language='en',
            transcript_type='auto',
            duration=10.0,
        )

        cache.set('abc123', result)

        # Get the data that was passed to Redis
        call_args = mock_redis_client.set.call_args
        stored_data = call_args[0][1]  # Second argument is the value

        # Should be valid JSON
        parsed = json.loads(stored_data)
        assert parsed['video_id'] == 'abc123'
        assert parsed['transcript'] == 'Hello world'
        assert parsed['language'] == 'en'
        assert parsed['transcript_type'] == 'auto'
        assert parsed['duration'] == 10.0

    @patch('youtube_transcript.services.cache.redis.Redis')
    def test_set_applies_ttl_to_cache_entry(self, mock_redis):
        """Test that set() applies TTL to the cache entry."""
        mock_redis_client = Mock()
        mock_redis.return_value = mock_redis_client

        cache = TranscriptCache(ttl=3600)
        result = TranscriptResult(
            video_id='test123',
            transcript='Test',
            language='en',
            transcript_type='manual',
            duration=5.0,
        )

        cache.set('test123', result)

        # Verify expire was called with correct TTL
        mock_redis_client.expire.assert_called_once()
        call_args = mock_redis_client.expire.call_args
        assert call_args[0][1] == 3600  # TTL value

    @patch('youtube_transcript.services.cache.redis.Redis')
    def test_set_handles_long_transcript_text(self, mock_redis):
        """Test that set() handles long transcript text correctly."""
        mock_redis_client = Mock()
        mock_redis.return_value = mock_redis_client

        cache = TranscriptCache()
        long_text = 'Lorem ipsum ' * 1000  # Long transcript

        result = TranscriptResult(
            video_id='long123',
            transcript=long_text,
            language='en',
            transcript_type='auto',
            duration=600.0,
        )

        cache.set('long123', result)

        # Verify it was stored without errors
        mock_redis_client.set.assert_called_once()

    @patch('youtube_transcript.services.cache.redis.Redis')
    def test_set_handles_unicode_characters(self, mock_redis):
        """Test that set() handles unicode characters correctly."""
        mock_redis_client = Mock()
        mock_redis.return_value = mock_redis_client

        cache = TranscriptCache()
        unicode_text = 'Test with émojis 🎉 and spëcial çharacters 你好'

        result = TranscriptResult(
            video_id='unicode123',
            transcript=unicode_text,
            language='en',
            transcript_type='manual',
            duration=30.0,
        )

        cache.set('unicode123', result)

        # Verify storage
        mock_redis_client.set.assert_called_once()
        call_args = mock_redis_client.set.call_args
        stored_data = call_args[0][1]
        parsed = json.loads(stored_data)
        assert 'émojis 🎉' in parsed['transcript']


class TestCacheGetOperations:
    """Test cache get operations."""

    @patch('youtube_transcript.services.cache.redis.Redis')
    def test_get_retrieves_cached_transcript(self, mock_redis):
        """Test that get() retrieves a cached transcript."""
        result_data = {
            'video_id': 'test123',
            'transcript': 'Sample transcript',
            'language': 'en',
            'transcript_type': 'manual',
            'duration': 120.5,
        }

        mock_redis_client = Mock()
        mock_redis_client.get.return_value = json.dumps(result_data).encode('utf-8')
        mock_redis.return_value = mock_redis_client

        cache = TranscriptCache()
        result = cache.get('test123')

        assert result is not None
        assert result.video_id == 'test123'
        assert result.transcript == 'Sample transcript'
        assert result.language == 'en'
        assert result.transcript_type == 'manual'
        assert result.duration == 120.5

    @patch('youtube_transcript.services.cache.redis.Redis')
    def test_get_returns_none_for_cache_miss(self, mock_redis):
        """Test that get() returns None when transcript is not cached."""
        mock_redis_client = Mock()
        mock_redis_client.get.return_value = None
        mock_redis.return_value = mock_redis_client

        cache = TranscriptCache()
        result = cache.get('nonexistent')

        assert result is None

    @patch('youtube_transcript.services.cache.redis.Redis')
    def test_get_deserializes_json_to_transcript_result(self, mock_redis):
        """Test that get() properly deserializes JSON to TranscriptResult."""
        result_data = {
            'video_id': 'abc123',
            'transcript': 'Test transcript',
            'language': 'es',
            'transcript_type': 'auto',
            'duration': 45.7,
        }

        mock_redis_client = Mock()
        mock_redis_client.get.return_value = json.dumps(result_data).encode('utf-8')
        mock_redis.return_value = mock_redis_client

        cache = TranscriptCache()
        result = cache.get('abc123')

        assert isinstance(result, TranscriptResult)
        assert result.video_id == 'abc123'
        assert result.transcript == 'Test transcript'
        assert result.language == 'es'
        assert result.transcript_type == 'auto'
        assert result.duration == 45.7

    @patch('youtube_transcript.services.cache.redis.Redis')
    def test_get_handles_corrupted_json_gracefully(self, mock_redis):
        """Test that get() handles corrupted JSON gracefully."""
        mock_redis_client = Mock()
        mock_redis_client.get.return_value = b'invalid json{{{'
        mock_redis.return_value = mock_redis_client

        cache = TranscriptCache()
        result = cache.get('corrupted')

        # Should return None for corrupted data
        assert result is None

    @patch('youtube_transcript.services.cache.redis.Redis')
    def test_get_handles_missing_fields(self, mock_redis):
        """Test that get() handles JSON with missing fields gracefully."""
        # Incomplete data (missing duration field)
        incomplete_data = {
            'video_id': 'test123',
            'transcript': 'Test',
            'language': 'en',
            # 'transcript_type' and 'duration' missing
        }

        mock_redis_client = Mock()
        mock_redis_client.get.return_value = json.dumps(incomplete_data).encode('utf-8')
        mock_redis.return_value = mock_redis_client

        cache = TranscriptCache()
        result = cache.get('test123')

        # Should still return a result with defaults for missing fields
        # or handle gracefully - implementation dependent


class TestCacheDeleteOperations:
    """Test cache delete operations."""

    @patch('youtube_transcript.services.cache.redis.Redis')
    def test_delete_removes_cached_transcript(self, mock_redis):
        """Test that delete() removes a transcript from cache."""
        mock_redis_client = Mock()
        mock_redis_client.delete.return_value = 1  # 1 item deleted
        mock_redis.return_value = mock_redis_client

        cache = TranscriptCache()
        deleted = cache.delete('test123')

        assert deleted is True
        mock_redis_client.delete.assert_called_once()

    @patch('youtube_transcript.services.cache.redis.Redis')
    def test_delete_returns_false_for_nonexistent_key(self, mock_redis):
        """Test that delete() returns False for nonexistent key."""
        mock_redis_client = Mock()
        mock_redis_client.delete.return_value = 0  # 0 items deleted
        mock_redis.return_value = mock_redis_client

        cache = TranscriptCache()
        deleted = cache.delete('nonexistent')

        assert deleted is False


class TestCacheExistsOperations:
    """Test cache exists operations."""

    @patch('youtube_transcript.services.cache.redis.Redis')
    def test_exists_returns_true_for_cached_transcript(self, mock_redis):
        """Test that exists() returns True for cached transcript."""
        mock_redis_client = Mock()
        mock_redis_client.exists.return_value = 1
        mock_redis.return_value = mock_redis_client

        cache = TranscriptCache()
        exists = cache.exists('test123')

        assert exists is True
        mock_redis_client.exists.assert_called_once()

    @patch('youtube_transcript.services.cache.redis.Redis')
    def test_exists_returns_false_for_uncached_transcript(self, mock_redis):
        """Test that exists() returns False for uncached transcript."""
        mock_redis_client = Mock()
        mock_redis_client.exists.return_value = 0
        mock_redis.return_value = mock_redis_client

        cache = TranscriptCache()
        exists = cache.exists('nonexistent')

        assert exists is False


class TestCacheClearOperations:
    """Test cache clear operations."""

    @patch('youtube_transcript.services.cache.redis.Redis')
    def test_clear_all_removes_all_transcripts(self, mock_redis):
        """Test that clear_all() removes all cached transcripts."""
        mock_redis_client = Mock()
        mock_redis_client.keys.return_value = [
            b'ytt:transcript:video1',
            b'ytt:transcript:video2',
            b'ytt:transcript:video3',
        ]
        mock_redis_client.delete.return_value = 3
        mock_redis.return_value = mock_redis_client

        cache = TranscriptCache(prefix='ytt')
        cleared = cache.clear_all()

        assert cleared is True
        mock_redis_client.keys.assert_called_once()
        mock_redis_client.delete.assert_called_once()

    @patch('youtube_transcript.services.cache.redis.Redis')
    def test_clear_all_handles_empty_cache(self, mock_redis):
        """Test that clear_all() handles empty cache gracefully."""
        mock_redis_client = Mock()
        mock_redis_client.keys.return_value = []
        mock_redis.return_value = mock_redis_client

        cache = TranscriptCache()
        cleared = cache.clear_all()

        assert cleared is True


class TestCacheStatistics:
    """Test cache statistics and monitoring."""

    @patch('youtube_transcript.services.cache.redis.Redis')
    def test_get_stats_returns_cache_statistics(self, mock_redis):
        """Test that get_stats() returns cache statistics."""
        mock_redis_client = Mock()
        mock_redis_client.dbsize.return_value = 100
        mock_redis_client.info.return_value = {
            'used_memory': '1024000',
            'used_memory_human': '1.00M',
        }
        mock_redis.return_value = mock_redis_client

        cache = TranscriptCache()
        stats = cache.get_stats()

        assert stats is not None
        assert 'total_keys' in stats or 'db_size' in stats


class TestCacheErrorHandling:
    """Test error handling in cache operations."""

    @patch('youtube_transcript.services.cache.redis.Redis')
    def test_set_handles_redis_connection_error(self, mock_redis):
        """Test that set() handles Redis connection errors gracefully."""
        mock_redis_client = Mock()
        mock_redis_client.set.side_effect = Exception('Connection refused')
        mock_redis.return_value = mock_redis_client

        cache = TranscriptCache()
        result = TranscriptResult(
            video_id='test123',
            transcript='Test',
            language='en',
            transcript_type='manual',
            duration=10.0,
        )

        # Should handle error gracefully
        cache.set('test123', result)

    @patch('youtube_transcript.services.cache.redis.Redis')
    def test_get_handles_redis_connection_error(self, mock_redis):
        """Test that get() handles Redis connection errors gracefully."""
        mock_redis_client = Mock()
        mock_redis_client.get.side_effect = Exception('Connection refused')
        mock_redis.return_value = mock_redis_client

        cache = TranscriptCache()
        result = cache.get('test123')

        # Should return None on error
        assert result is None


class TestCacheIntegration:
    """Test cache integration scenarios."""

    @patch('youtube_transcript.services.cache.redis.Redis')
    def test_cache_hit_scenario(self, mock_redis):
        """Test complete cache hit scenario: set -> get -> verify."""
        mock_redis_client = Mock()

        # Setup: First get returns None (miss), then returns data (hit)
        result_data = {
            'video_id': 'test123',
            'transcript': 'Cached transcript',
            'language': 'en',
            'transcript_type': 'manual',
            'duration': 100.0,
        }

        mock_redis_client.get.return_value = json.dumps(result_data).encode('utf-8')
        mock_redis.return_value = mock_redis_client

        cache = TranscriptCache()

        # Set the cache
        result = TranscriptResult(**result_data)
        cache.set('test123', result)

        # Get from cache
        retrieved = cache.get('test123')

        assert retrieved is not None
        assert retrieved.video_id == 'test123'
        assert retrieved.transcript == 'Cached transcript'

    @patch('youtube_transcript.services.cache.redis.Redis')
    def test_cache_miss_scenario(self, mock_redis):
        """Test complete cache miss scenario: get None -> set -> get data."""
        mock_redis_client = Mock()
        mock_redis_client.get.return_value = None  # Cache miss
        mock_redis.return_value = mock_redis_client

        cache = TranscriptCache()

        # First get - cache miss
        result = cache.get('new_video')
        assert result is None

        # Now set the cache
        new_result = TranscriptResult(
            video_id='new_video',
            transcript='New transcript',
            language='en',
            transcript_type='auto',
            duration=50.0,
        )
        cache.set('new_video', new_result)

        # Verify it was stored
        mock_redis_client.set.assert_called_once()


class TestCacheTtlBehavior:
    """Test TTL and expiration behavior."""

    @patch('youtube_transcript.services.cache.redis.Redis')
    def test_get_ttl_returns_remaining_ttl(self, mock_redis):
        """Test that get_ttl() returns remaining TTL for cached item."""
        mock_redis_client = Mock()
        mock_redis_client.ttl.return_value = 3600  # 1 hour remaining
        mock_redis.return_value = mock_redis_client

        cache = TranscriptCache()
        ttl = cache.get_ttl('test123')

        assert ttl == 3600
        mock_redis_client.ttl.assert_called_once()

    @patch('youtube_transcript.services.cache.redis.Redis')
    def test_get_ttl_returns_negative_for_expired(self, mock_redis):
        """Test that get_ttl() returns negative value for expired/nonexistent items."""
        mock_redis_client = Mock()
        mock_redis_client.ttl.return_value = -2  # Key does not exist
        mock_redis.return_value = mock_redis_client

        cache = TranscriptCache()
        ttl = cache.get_ttl('nonexistent')

        assert ttl < 0
