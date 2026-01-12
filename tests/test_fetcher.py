"""
Test YouTube transcript fetcher.

These tests verify that YouTubeTranscriptFetcher can fetch transcripts from YouTube.
Following TDD: Write tests first, watch them fail, then implement to pass.
"""

from unittest.mock import Mock, patch
import pytest

from youtube_transcript.services.fetcher import (
    YouTubeTranscriptFetcher,
    TranscriptFetchError,
    TranscriptUnavailableError,
    VideoUnavailableError,
)


class TestTranscriptFetcherCreation:
    """Test fetcher instantiation and initialization."""

    def test_fetcher_can_be_created(self):
        """Test that YouTubeTranscriptFetcher can be instantiated."""
        fetcher = YouTubeTranscriptFetcher()
        assert fetcher is not None


class TestFetchTranscript:
    """Test transcript fetching functionality."""

    @patch('youtube_transcript.services.fetcher.YouTubeTranscriptApi')
    def test_fetch_transcript_from_real_video(self, mock_youtube_api):
        """Test fetching transcript from a real video (with mocked API)."""
        # Mock the YouTube transcript API response - using new fetch() API structure
        mock_snippets = [
            Mock(text='Hello world', start=0.0, duration=1.0),
            Mock(text='This is a test', start=1.0, duration=2.0),
        ]
        mock_fetched = Mock(
            video_id='dQw4w9WgXcQ',
            language_code='en',
            is_generated=False,
            snippets=mock_snippets
        )
        mock_youtube_api.return_value.fetch.return_value = mock_fetched

        fetcher = YouTubeTranscriptFetcher()
        result = fetcher.fetch_transcript('dQw4w9WgXcQ')

        assert result is not None
        assert result.video_id == 'dQw4w9WgXcQ'
        assert result.transcript == 'Hello world This is a test'
        assert result.language == 'en'
        assert 'manual' in result.transcript_type.lower() or 'auto' in result.transcript_type.lower()

    @patch('youtube_transcript.services.fetcher.YouTubeTranscriptApi')
    def test_fetch_with_language_preference(self, mock_youtube_api):
        """Test that language preference is respected."""
        mock_snippets = [
            Mock(text='Hola mundo', start=0.0, duration=1.0),
        ]
        mock_fetched = Mock(
            video_id='test123',
            language_code='es',
            is_generated=False,
            snippets=mock_snippets
        )
        mock_youtube_api.return_value.fetch.return_value = mock_fetched

        fetcher = YouTubeTranscriptFetcher()
        result = fetcher.fetch_transcript('test123', languages=['es'])

        assert result is not None
        assert result.video_id == 'test123'
        # Verify the API was called with the correct language
        mock_youtube_api.return_value.fetch.assert_called_once_with('test123', languages=['es'])

    @patch('youtube_transcript.services.fetcher.YouTubeTranscriptApi')
    def test_fetch_preserves_metadata(self, mock_youtube_api):
        """Test that fetcher captures transcript metadata."""
        mock_snippets = [
            Mock(text='Test', start=0.0, duration=1.0),
        ]
        mock_fetched = Mock(
            video_id='test123',
            language_code='en',
            is_generated=False,
            snippets=mock_snippets
        )
        mock_youtube_api.return_value.fetch.return_value = mock_fetched

        fetcher = YouTubeTranscriptFetcher()
        result = fetcher.fetch_transcript('test123')

        assert result is not None
        assert hasattr(result, 'language')
        assert hasattr(result, 'transcript_type')
        assert hasattr(result, 'duration')


class TestErrorHandling:
    """Test error handling for various failure scenarios."""

    @patch('youtube_transcript.services.fetcher.YouTubeTranscriptApi')
    def test_transcript_disabled_returns_none(self, mock_youtube_api):
        """Test handling of videos without transcripts (TranscriptsDisabled exception)."""
        from youtube_transcript_api import TranscriptsDisabled

        mock_youtube_api.return_value.fetch.side_effect = TranscriptsDisabled('No transcripts')

        fetcher = YouTubeTranscriptFetcher()
        result = fetcher.fetch_transcript('video_without_transcript')

        assert result is None

    @patch('youtube_transcript.services.fetcher.YouTubeTranscriptApi')
    def test_video_unavailable_returns_none(self, mock_youtube_api):
        """Test handling of private/deleted videos (VideoUnavailable exception)."""
        from youtube_transcript_api import VideoUnavailable

        mock_youtube_api.return_value.fetch.side_effect = VideoUnavailable('Video not found')

        fetcher = YouTubeTranscriptFetcher()
        result = fetcher.fetch_transcript('private_video')

        assert result is None

    @patch('youtube_transcript.services.fetcher.YouTubeTranscriptApi')
    def test_generic_exception_raises_fetch_error(self, mock_youtube_api):
        """Test that unexpected exceptions are wrapped in TranscriptFetchError."""
        mock_youtube_api.return_value.fetch.side_effect = Exception('Network error')

        fetcher = YouTubeTranscriptFetcher()

        with pytest.raises(TranscriptFetchError) as exc_info:
            fetcher.fetch_transcript('test123')

        assert 'Failed to fetch transcript' in str(exc_info.value)
        assert 'test123' in str(exc_info.value)

    @patch('youtube_transcript.services.fetcher.YouTubeTranscriptApi')
    def test_rate_limiting_returns_none(self, mock_youtube_api):
        """Test handling of rate limiting (should be graceful)."""
        from youtube_transcript_api import YouTubeTranscriptApiException

        mock_youtube_api.return_value.fetch.side_effect = YouTubeTranscriptApiException('Rate limited')

        fetcher = YouTubeTranscriptFetcher()
        result = fetcher.fetch_transcript('rate_limited_video')

        # Should handle gracefully and return None
        assert result is None


class TestTranscriptDataParsing:
    """Test parsing of transcript data returned by YouTube API."""

    @patch('youtube_transcript.services.fetcher.YouTubeTranscriptApi')
    def test_empty_transcript_list(self, mock_youtube_api):
        """Test handling of empty transcript list."""
        mock_fetched = Mock(
            video_id='test123',
            language_code='en',
            is_generated=False,
            snippets=[]
        )
        mock_youtube_api.return_value.fetch.return_value = mock_fetched

        fetcher = YouTubeTranscriptFetcher()
        result = fetcher.fetch_transcript('test123')

        # Should return None for empty transcript
        assert result is None

    @patch('youtube_transcript.services.fetcher.YouTubeTranscriptApi')
    def test_transcript_with_timestamps(self, mock_youtube_api):
        """Test that transcript text is concatenated correctly."""
        mock_snippets = [
            Mock(text='First', start=0.0, duration=1.0),
            Mock(text='Second', start=1.0, duration=1.0),
            Mock(text='Third', start=2.0, duration=1.0),
        ]
        mock_fetched = Mock(
            video_id='test123',
            language_code='en',
            is_generated=False,
            snippets=mock_snippets
        )
        mock_youtube_api.return_value.fetch.return_value = mock_fetched

        fetcher = YouTubeTranscriptFetcher()
        result = fetcher.fetch_transcript('test123')

        assert result.transcript == 'First Second Third'

    @patch('youtube_transcript.services.fetcher.YouTubeTranscriptApi')
    def test_transcript_type_detection(self, mock_youtube_api):
        """Test detection of manual vs auto-generated transcripts."""
        # Test with manual transcript (no generation info)
        mock_snippets = [
            Mock(text='Manual transcript', start=0.0, duration=1.0),
        ]
        mock_fetched = Mock(
            video_id='manual_video',
            language_code='en',
            is_generated=False,
            snippets=mock_snippets
        )
        mock_youtube_api.return_value.fetch.return_value = mock_fetched

        fetcher = YouTubeTranscriptFetcher()
        result = fetcher.fetch_transcript('manual_video')

        assert result.transcript_type == 'manual'

    @patch('youtube_transcript.services.fetcher.YouTubeTranscriptApi')
    def test_auto_generated_transcript_detection(self, mock_youtube_api):
        """Test detection of auto-generated transcripts."""
        mock_snippets = [
            Mock(text='Auto generated', start=0.0, duration=1.0),
        ]
        mock_fetched = Mock(
            video_id='auto_video',
            language_code='en',
            is_generated=True,
            snippets=mock_snippets
        )
        mock_youtube_api.return_value.fetch.return_value = mock_fetched

        fetcher = YouTubeTranscriptFetcher()
        result = fetcher.fetch_transcript('auto_video')

        assert result.transcript_type == 'auto'


class TestTranscriptResultModel:
    """Test the TranscriptResult data model."""

    @patch('youtube_transcript.services.fetcher.YouTubeTranscriptApi')
    def test_transcript_result_has_all_fields(self, mock_youtube_api):
        """Test that TranscriptResult contains all required fields."""
        mock_snippets = [
            Mock(text='Test transcript', start=0.0, duration=1.0),
        ]
        mock_fetched = Mock(
            video_id='test123',
            language_code='en',
            is_generated=False,
            snippets=mock_snippets
        )
        mock_youtube_api.return_value.fetch.return_value = mock_fetched

        fetcher = YouTubeTranscriptFetcher()
        result = fetcher.fetch_transcript('test123')

        # Verify all required fields
        assert hasattr(result, 'video_id')
        assert hasattr(result, 'transcript')
        assert hasattr(result, 'language')
        assert hasattr(result, 'transcript_type')
        assert hasattr(result, 'duration')

    @patch('youtube_transcript.services.fetcher.YouTubeTranscriptApi')
    def test_transcript_result_field_types(self, mock_youtube_api):
        """Test that TranscriptResult fields have correct types."""
        mock_snippets = [
            Mock(text='Test', start=0.0, duration=1.0),
        ]
        mock_fetched = Mock(
            video_id='test123',
            language_code='en',
            is_generated=False,
            snippets=mock_snippets
        )
        mock_youtube_api.return_value.fetch.return_value = mock_fetched

        fetcher = YouTubeTranscriptFetcher()
        result = fetcher.fetch_transcript('test123')

        assert isinstance(result.video_id, str)
        assert isinstance(result.transcript, str)
        assert isinstance(result.language, str)
        assert isinstance(result.transcript_type, str)


class TestMultipleLanguages:
    """Test handling of multi-language transcripts."""

    @patch('youtube_transcript.services.fetcher.YouTubeTranscriptApi')
    def test_fetch_with_multiple_language_fallback(self, mock_youtube_api):
        """Test fetching with multiple language preferences."""
        # The youtube-transcript-api handles language fallback internally
        # We just pass the language list to the API
        mock_snippets = [
            Mock(text='English text', start=0.0, duration=1.0),
        ]
        mock_fetched = Mock(
            video_id='test123',
            language_code='en',
            is_generated=False,
            snippets=mock_snippets
        )
        mock_youtube_api.return_value.fetch.return_value = mock_fetched

        fetcher = YouTubeTranscriptFetcher()
        # Try multiple languages - API will handle fallback
        result = fetcher.fetch_transcript('test123', languages=['fr', 'es', 'en'])

        assert result is not None
        assert 'English' in result.transcript
        # Verify the API was called with the language list
        mock_youtube_api.return_value.fetch.assert_called_once_with('test123', languages=['fr', 'es', 'en'])
