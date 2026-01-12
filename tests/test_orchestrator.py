"""
Test transcript service orchestrator.

These tests verify that TranscriptOrchestrator coordinates between
fetcher, cache, and repository to provide a unified transcript retrieval API.
Following TDD: Write tests first, watch them fail, then implement to pass.
"""

from unittest.mock import Mock, patch
import pytest

from youtube_transcript.services.fetcher import TranscriptResult
from youtube_transcript.services.orchestrator import TranscriptOrchestrator


class TestTranscriptOrchestratorCreation:
    """Test orchestrator instantiation and initialization."""

    def test_orchestrator_can_be_created(self, test_db):
        """Test that TranscriptOrchestrator can be instantiated."""
        mock_cache = Mock()
        orchestrator = TranscriptOrchestrator(
            session=test_db,
            cache=mock_cache,
        )
        assert orchestrator is not None
        assert orchestrator.fetcher is not None
        assert orchestrator.cache is not None
        assert orchestrator.repository is not None


class TestGetTranscriptCacheHit:
    """Test transcript retrieval with cache hits."""

    def test_get_transcript_from_cache(self, test_db):
        """Test that get_transcript() retrieves from cache when available."""
        # Setup: Mock cache to return a transcript
        cached_result = TranscriptResult(
            video_id='test123',
            transcript='Cached transcript',
            language='en',
            transcript_type='manual',
            duration=100.0,
        )
        mock_cache = Mock()
        mock_cache.get.return_value = cached_result

        orchestrator = TranscriptOrchestrator(
            session=test_db,
            cache=mock_cache,
        )

        result = orchestrator.get_transcript('test123')

        assert result is not None
        assert result.transcript == 'Cached transcript'
        # Should call cache.get
        mock_cache.get.assert_called_once_with('test123')
        # Should NOT call repository or fetcher
        mock_cache.set.assert_not_called()

    def test_cache_hit_skips_database_and_api(self, test_db):
        """Test that cache hit skips database and API calls."""
        cached_result = TranscriptResult(
            video_id='test123',
            transcript='From cache',
            language='en',
            transcript_type='manual',
            duration=50.0,
        )
        mock_cache = Mock()
        mock_cache.get.return_value = cached_result

        orchestrator = TranscriptOrchestrator(
            session=test_db,
            cache=mock_cache,
        )

        result = orchestrator.get_transcript('test123')

        assert result is not None
        assert result.transcript == 'From cache'
        # Verify only cache.get was called
        mock_cache.get.assert_called_once()
        # Cache should not be updated
        mock_cache.set.assert_not_called()


class TestGetTranscriptDatabaseHit:
    """Test transcript retrieval with database hits (cache miss)."""

    def test_get_transcript_from_database(self, test_db):
        """Test that get_transcript() retrieves from database when cache misses."""
        # Setup: Cache miss, database hit
        mock_cache = Mock()
        mock_cache.get.return_value = None  # Cache miss

        # Create a transcript in the database
        from youtube_transcript.services import TranscriptRepository
        repository = TranscriptRepository(test_db)
        db_result = TranscriptResult(
            video_id='test123',
            transcript='Database transcript',
            language='en',
            transcript_type='manual',
            duration=100.0,
        )
        repository.create(db_result)

        orchestrator = TranscriptOrchestrator(
            session=test_db,
            cache=mock_cache,
        )

        result = orchestrator.get_transcript('test123')

        assert result is not None
        assert result.transcript == 'Database transcript'
        # Should update cache
        mock_cache.set.assert_called_once()

    def test_database_hit_updates_cache(self, test_db):
        """Test that database hit populates the cache."""
        mock_cache = Mock()
        mock_cache.get.return_value = None  # Cache miss

        # Create transcript in database
        from youtube_transcript.services import TranscriptRepository
        repository = TranscriptRepository(test_db)
        db_result = TranscriptResult(
            video_id='test123',
            transcript='DB transcript',
            language='en',
            transcript_type='auto',
            duration=75.0,
        )
        repository.create(db_result)

        orchestrator = TranscriptOrchestrator(
            session=test_db,
            cache=mock_cache,
        )

        result = orchestrator.get_transcript('test123')

        assert result is not None
        # Verify cache was updated
        mock_cache.set.assert_called_once()


class TestGetTranscriptAPIFetch:
    """Test transcript retrieval from API (cache and database miss)."""

    @patch('youtube_transcript.services.orchestrator.YouTubeTranscriptFetcher')
    def test_get_transcript_from_api(self, mock_fetcher_class, test_db):
        """Test that get_transcript() fetches from API when cache and DB miss."""
        # Setup: Cache miss, database miss, API success
        mock_cache = Mock()
        mock_cache.get.return_value = None  # Cache miss

        # Mock fetcher to return a transcript
        api_result = TranscriptResult(
            video_id='test123',
            transcript='API transcript',
            language='en',
            transcript_type='manual',
            duration=100.0,
        )
        mock_fetcher_instance = mock_fetcher_class.return_value
        mock_fetcher_instance.fetch_transcript.return_value = api_result

        orchestrator = TranscriptOrchestrator(
            session=test_db,
            cache=mock_cache,
            fetcher=mock_fetcher_instance,
        )

        result = orchestrator.get_transcript('test123')

        assert result is not None
        assert result.transcript == 'API transcript'
        # Should call fetcher
        mock_fetcher_instance.fetch_transcript.assert_called_once_with('test123', languages=None)
        # Should update cache
        mock_cache.set.assert_called_once()
        # Should save to database
        from youtube_transcript.services import TranscriptRepository
        repository = TranscriptRepository(test_db)
        db_transcript = repository.get_by_video_id('test123')
        assert db_transcript is not None

    @patch('youtube_transcript.services.orchestrator.YouTubeTranscriptFetcher')
    def test_api_fetch_populates_cache_and_database(self, mock_fetcher_class, test_db):
        """Test that API fetch populates both cache and database."""
        mock_cache = Mock()
        mock_cache.get.return_value = None  # Cache and database miss

        api_result = TranscriptResult(
            video_id='new123',
            transcript='Fresh from API',
            language='en',
            transcript_type='manual',
            duration=60.0,
        )
        mock_fetcher_instance = mock_fetcher_class.return_value
        mock_fetcher_instance.fetch_transcript.return_value = api_result

        orchestrator = TranscriptOrchestrator(
            session=test_db,
            cache=mock_cache,
            fetcher=mock_fetcher_instance,
        )

        result = orchestrator.get_transcript('new123')

        assert result is not None
        # Verify cache was populated
        mock_cache.set.assert_called_once()
        # Verify database was populated
        from youtube_transcript.services import TranscriptRepository
        repository = TranscriptRepository(test_db)
        db_transcript = repository.get_by_video_id('new123')
        assert db_transcript is not None
        assert db_transcript.transcript_text == 'Fresh from API'


class TestGetTranscriptNotFound:
    """Test transcript retrieval when transcript doesn't exist."""

    @patch('youtube_transcript.services.orchestrator.YouTubeTranscriptFetcher')
    def test_get_transcript_returns_none_when_not_found(self, mock_fetcher_class, test_db):
        """Test that get_transcript() returns None when transcript not found anywhere."""
        # Setup: Cache miss, database miss, API returns None
        mock_cache = Mock()
        mock_cache.get.return_value = None  # Cache miss
        mock_fetcher_instance = mock_fetcher_class.return_value
        mock_fetcher_instance.fetch_transcript.return_value = None  # API miss

        orchestrator = TranscriptOrchestrator(
            session=test_db,
            cache=mock_cache,
            fetcher=mock_fetcher_instance,
        )

        result = orchestrator.get_transcript('nonexistent')

        assert result is None
        # Should try fetcher
        mock_fetcher_instance.fetch_transcript.assert_called_once()
        # Should NOT update cache
        mock_cache.set.assert_not_called()


class TestGetTranscriptWithLanguage:
    """Test transcript retrieval with language preferences."""

    @patch('youtube_transcript.services.orchestrator.YouTubeTranscriptFetcher')
    def test_get_transcript_with_language_preference(self, mock_fetcher_class, test_db):
        """Test that language preference is passed to fetcher."""
        mock_cache = Mock()
        mock_cache.get.return_value = None  # Cache and database miss

        api_result = TranscriptResult(
            video_id='test123',
            transcript='Spanish transcript',
            language='es',
            transcript_type='manual',
            duration=80.0,
        )
        mock_fetcher_instance = mock_fetcher_class.return_value
        mock_fetcher_instance.fetch_transcript.return_value = api_result

        orchestrator = TranscriptOrchestrator(
            session=test_db,
            cache=mock_cache,
            fetcher=mock_fetcher_instance,
        )

        result = orchestrator.get_transcript('test123', languages=['es'])

        assert result is not None
        assert result.language == 'es'
        # Verify language was passed to fetcher
        mock_fetcher_instance.fetch_transcript.assert_called_once_with('test123', languages=['es'])


class TestInvalidateCache:
    """Test cache invalidation operations."""

    def test_invalidate_cache_removes_from_cache(self, test_db):
        """Test that invalidate_cache() removes transcript from cache."""
        mock_cache = Mock()
        mock_cache.delete.return_value = True

        orchestrator = TranscriptOrchestrator(
            session=test_db,
            cache=mock_cache,
        )

        result = orchestrator.invalidate_cache('test123')

        assert result is True
        mock_cache.delete.assert_called_once_with('test123')

    def test_invalidate_cache_returns_false_when_not_cached(self, test_db):
        """Test that invalidate_cache() returns False when transcript not in cache."""
        mock_cache = Mock()
        mock_cache.delete.return_value = False

        orchestrator = TranscriptOrchestrator(
            session=test_db,
            cache=mock_cache,
        )

        result = orchestrator.invalidate_cache('test123')

        assert result is False


class TestPrefetch:
    """Test prefetch operations."""

    @patch('youtube_transcript.services.orchestrator.YouTubeTranscriptFetcher')
    def test_prefetch_fetches_and_caches_transcript(self, mock_fetcher_class, test_db):
        """Test that prefetch() fetches and caches a transcript."""
        mock_cache = Mock()
        api_result = TranscriptResult(
            video_id='test123',
            transcript='Prefetched',
            language='en',
            transcript_type='manual',
            duration=90.0,
        )
        mock_fetcher_instance = mock_fetcher_class.return_value
        mock_fetcher_instance.fetch_transcript.return_value = api_result

        orchestrator = TranscriptOrchestrator(
            session=test_db,
            cache=mock_cache,
            fetcher=mock_fetcher_instance,
        )

        result = orchestrator.prefetch('test123')

        assert result is not None
        assert result.transcript == 'Prefetched'
        # Should be cached
        mock_cache.set.assert_called_once()
        # Should be in database
        from youtube_transcript.services import TranscriptRepository
        repository = TranscriptRepository(test_db)
        db_transcript = repository.get_by_video_id('test123')
        assert db_transcript is not None

    @patch('youtube_transcript.services.orchestrator.YouTubeTranscriptFetcher')
    def test_prefetch_returns_none_when_not_found(self, mock_fetcher_class, test_db):
        """Test that prefetch() returns None when transcript doesn't exist."""
        mock_cache = Mock()
        mock_fetcher_instance = mock_fetcher_class.return_value
        mock_fetcher_instance.fetch_transcript.return_value = None

        orchestrator = TranscriptOrchestrator(
            session=test_db,
            cache=mock_cache,
            fetcher=mock_fetcher_instance,
        )

        result = orchestrator.prefetch('nonexistent')

        assert result is None
        # Should NOT cache or save
        mock_cache.set.assert_not_called()


class TestClearCache:
    """Test cache clearing operations."""

    def test_clear_cache_clears_all_transcripts(self, test_db):
        """Test that clear_cache() clears all cached transcripts."""
        mock_cache = Mock()
        mock_cache.clear_all.return_value = True

        orchestrator = TranscriptOrchestrator(
            session=test_db,
            cache=mock_cache,
        )

        result = orchestrator.clear_cache()

        assert result is True
        mock_cache.clear_all.assert_called_once()


class TestGetStatistics:
    """Test statistics and monitoring operations."""

    def test_get_statistics_returns_metrics(self, test_db):
        """Test that get_statistics() returns cache and database statistics."""
        # Setup mock data
        mock_cache = Mock()
        mock_cache.get_stats.return_value = {
            'total_keys': 100,
            'memory_human': '10.00M',
        }

        # Create some transcripts in database
        from youtube_transcript.services import TranscriptRepository
        repository = TranscriptRepository(test_db)
        repository.create(TranscriptResult(
            video_id='test1',
            transcript='Test 1',
            language='en',
            transcript_type='manual',
            duration=10.0,
        ))
        repository.create(TranscriptResult(
            video_id='test2',
            transcript='Test 2',
            language='en',
            transcript_type='manual',
            duration=10.0,
        ))

        orchestrator = TranscriptOrchestrator(
            session=test_db,
            cache=mock_cache,
        )

        stats = orchestrator.get_statistics()

        assert stats is not None
        assert 'cache_keys' in stats
        assert 'database_count' in stats
        assert stats['cache_keys'] == 100
        assert stats['database_count'] >= 2


class TestErrorHandling:
    """Test error handling in orchestrator operations."""

    def test_handles_cache_errors_gracefully(self, test_db):
        """Test that cache errors don't prevent fallback to database."""
        # Cache throws error
        mock_cache = Mock()
        mock_cache.get.side_effect = Exception('Redis connection error')

        # Create transcript in database
        from youtube_transcript.services import TranscriptRepository
        repository = TranscriptRepository(test_db)
        db_result = TranscriptResult(
            video_id='test123',
            transcript='DB transcript',
            language='en',
            transcript_type='manual',
            duration=100.0,
        )
        repository.create(db_result)

        orchestrator = TranscriptOrchestrator(
            session=test_db,
            cache=mock_cache,
        )

        # Should fall back to database
        result = orchestrator.get_transcript('test123')

        assert result is not None
        assert result.transcript == 'DB transcript'

    @patch('youtube_transcript.services.orchestrator.YouTubeTranscriptFetcher')
    def test_handles_fetcher_errors_gracefully(self, mock_fetcher_class, test_db):
        """Test that fetcher errors are handled gracefully."""
        mock_cache = Mock()
        mock_cache.get.return_value = None  # Cache and database miss

        # Fetcher throws error
        mock_fetcher_instance = mock_fetcher_class.return_value
        mock_fetcher_instance.fetch_transcript.side_effect = Exception('API error')

        orchestrator = TranscriptOrchestrator(
            session=test_db,
            cache=mock_cache,
            fetcher=mock_fetcher_instance,
        )

        # Should return None on error
        result = orchestrator.get_transcript('test123')

        # Should handle gracefully and return None
        assert result is None
