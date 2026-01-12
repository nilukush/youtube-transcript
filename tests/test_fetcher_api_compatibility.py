"""
Test youtube-transcript-api compatibility.

These tests verify that the fetcher works correctly with the current
version of youtube-transcript-api library (v1.0+).

Following TDD: These tests document the correct API usage after the
breaking change from get_transcript() to fetch().
"""

import pytest
from youtube_transcript_api import YouTubeTranscriptApi


class TestYouTubeTranscriptApiNewInterface:
    """Test the new youtube-transcript-api interface (v1.0+)."""

    def test_api_has_fetch_method(self):
        """Test that API has fetch method (not get_transcript)."""
        api = YouTubeTranscriptApi()
        assert hasattr(api, 'fetch'), "YouTubeTranscriptApi should have 'fetch' method"
        assert not hasattr(api, 'get_transcript'), "YouTubeTranscriptApi should NOT have deprecated 'get_transcript' method"

    def test_fetch_method_is_callable(self):
        """Test that fetch method is callable."""
        api = YouTubeTranscriptApi()
        assert callable(api.fetch), "fetch method should be callable"

    def test_fetch_returns_fetched_transcript_object(self):
        """Test that fetch() returns FetchedTranscript object."""
        api = YouTubeTranscriptApi()
        result = api.fetch('j9rZxAF3C0I', languages=('en',))

        # Should return FetchedTranscript object
        assert result is not None, "fetch() should return a result"
        assert hasattr(result, 'video_id'), "Result should have 'video_id' attribute"
        assert hasattr(result, 'snippets'), "Result should have 'snippets' attribute"
        assert hasattr(result, 'language_code'), "Result should have 'language_code' attribute"
        assert hasattr(result, 'is_generated'), "Result should have 'is_generated' attribute"

    def test_fetched_transcript_has_correct_attributes(self):
        """Test that FetchedTranscript has all expected attributes."""
        api = YouTubeTranscriptApi()
        result = api.fetch('j9rZxAF3C0I', languages=('en',))

        # Check all attributes
        assert result.video_id == 'j9rZxAF3C0I', "video_id should match"
        assert result.language_code == 'en', "language_code should be 'en'"
        assert isinstance(result.is_generated, bool), "is_generated should be boolean"
        assert isinstance(result.snippets, list), "snippets should be a list"
        assert len(result.snippets) > 0, "Should have at least one snippet"

    def test_snippets_have_correct_structure(self):
        """Test that snippets have text, duration, and start attributes."""
        api = YouTubeTranscriptApi()
        result = api.fetch('j9rZxAF3C0I', languages=('en',))

        snippet = result.snippets[0]
        assert hasattr(snippet, 'text'), "Snippet should have 'text' attribute"
        assert hasattr(snippet, 'duration'), "Snippet should have 'duration' attribute"
        assert hasattr(snippet, 'start'), "Snippet should have 'start' attribute"
        assert isinstance(snippet.text, str), "text should be string"
        assert isinstance(snippet.duration, float), "duration should be float"
        assert isinstance(snippet.start, float), "start should be float"

    def test_fetch_with_multiple_languages(self):
        """Test fetch with language preference list."""
        api = YouTubeTranscriptApi()
        result = api.fetch('j9rZxAF3C0I', languages=('en', 'es'))

        assert result is not None, "Should fetch transcript with language preference"
        assert result.video_id == 'j9rZxAF3C0I', "Should fetch correct video"

    def test_fetch_preserve_formatting_parameter(self):
        """Test that fetch accepts preserve_formatting parameter."""
        api = YouTubeTranscriptApi()
        result = api.fetch('j9rZxAF3C0I', languages=('en',), preserve_formatting=False)

        assert result is not None, "Should handle preserve_formatting parameter"

    def test_real_video_transcript_fetch(self):
        """Test fetching a real video transcript end-to-end."""
        api = YouTubeTranscriptApi()
        result = api.fetch('j9rZxAF3C0I', languages=('en',))

        # Verify we got actual content
        assert len(result.snippets) > 0, "Should have transcript snippets"

        # Concatenate all text
        full_text = ' '.join([s.text for s in result.snippets])
        assert len(full_text) > 100, "Transcript should have substantial content"
        assert len(full_text) > 0, "Transcript should not be empty"


class TestUserReportedVideos:
    """Test with the specific videos reported by the user."""

    def test_video_2S912iFJjkQ_has_transcript(self):
        """Test that user's first video has a transcript."""
        api = YouTubeTranscriptApi()
        result = api.fetch('2S912iFJjkQ', languages=('en',))

        assert result is not None, "Video 2S912iFJjkQ should have a transcript"
        assert len(result.snippets) > 0, "Should have transcript content"

    def test_video_FmSVuQoXjUQ_has_transcript(self):
        """Test that user's second video has a transcript."""
        api = YouTubeTranscriptApi()
        result = api.fetch('FmSVuQoXjUQ', languages=('en',))

        assert result is not None, "Video FmSVuQoXjUQ should have a transcript"
        assert len(result.snippets) > 0, "Should have transcript content"


class TestMigrationFromOldApi:
    """Test migration path from old get_transcript() to new fetch()."""

    def test_old_api_call_fails(self):
        """Test that the old get_transcript() method no longer exists."""
        api = YouTubeTranscriptApi()

        with pytest.raises(AttributeError, match="get_transcript"):
            api.get_transcript('j9rZxAF3C0I', languages=['en'])

    def test_new_api_call_succeeds(self):
        """Test that the new fetch() method works."""
        api = YouTubeTranscriptApi()
        result = api.fetch('j9rZxAF3C0I', languages=('en',))

        assert result is not None
        assert result.video_id == 'j9rZxAF3C0I'
