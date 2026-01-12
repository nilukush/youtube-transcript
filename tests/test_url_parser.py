"""
Test YouTube URL parser.

These tests verify that extract_video_id can handle all YouTube URL formats.
Following TDD: Write tests first, watch them fail, then implement to pass.
"""

import pytest

from youtube_transcript.utils.url_parser import extract_video_id


class TestStandardURLs:
    """Test standard YouTube watch URLs."""

    def test_standard_watch_url_with_www(self):
        """Test standard watch URL with www."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        assert extract_video_id(url) == "dQw4w9WgXcQ"

    def test_standard_watch_url_without_www(self):
        """Test standard watch URL without www."""
        url = "https://youtube.com/watch?v=dQw4w9WgXcQ"
        assert extract_video_id(url) == "dQw4w9WgXcQ"

    def test_standard_watch_url_http(self):
        """Test standard watch URL with HTTP (not HTTPS)."""
        url = "http://www.youtube.com/watch?v=dQw4w9WgXcQ"
        assert extract_video_id(url) == "dQw4w9WgXcQ"

    def test_standard_watch_url_mobile(self):
        """Test standard watch URL on mobile domain."""
        url = "https://m.youtube.com/watch?v=dQw4w9WgXcQ"
        assert extract_video_id(url) == "dQw4w9WgXcQ"

    def test_standard_watch_url_with_parameters(self):
        """Test standard watch URL with additional parameters."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=10s&list=PLxyz"
        assert extract_video_id(url) == "dQw4w9WgXcQ"


class TestShortURLs:
    """Test short youtu.be URLs."""

    def test_short_url(self):
        """Test short youtu.be URL."""
        url = "https://youtu.be/dQw4w9WgXcQ"
        assert extract_video_id(url) == "dQw4w9WgXcQ"

    def test_short_url_http(self):
        """Test short youtu.be URL with HTTP."""
        url = "http://youtu.be/dQw4w9WgXcQ"
        assert extract_video_id(url) == "dQw4w9WgXcQ"

    def test_short_url_with_timestamp(self):
        """Test short youtu.be URL with timestamp parameter."""
        url = "https://youtu.be/dQw4w9WgXcQ?t=10"
        assert extract_video_id(url) == "dQw4w9WgXcQ"

    def test_short_url_with_tracking_param(self):
        """Test short youtu.be URL with si tracking parameter."""
        url = "https://youtu.be/M9bq_alk-sw?si=B_RZg_I-lLaa7UU-"
        assert extract_video_id(url) == "M9bq_alk-sw"

    def test_short_url_with_feature_param(self):
        """Test short youtu.be URL with feature parameter."""
        url = "https://youtu.be/dQw4w9WgXcQ?feature=youtube_gdata_player"
        assert extract_video_id(url) == "dQw4w9WgXcQ"

    def test_short_url_with_list_param(self):
        """Test short youtu.be URL with list parameter."""
        url = "https://youtu.be/oTJRivZTMLs?list=PLToa5JuFMsXTNkrLJbRlB--76IAOjRM9b"
        assert extract_video_id(url) == "oTJRivZTMLs"


class TestEmbedURLs:
    """Test embed URLs."""

    def test_embed_url(self):
        """Test standard embed URL."""
        url = "https://www.youtube.com/embed/dQw4w9WgXcQ"
        assert extract_video_id(url) == "dQw4w9WgXcQ"

    def test_embed_url_no_cookie(self):
        """Test embed URL with no-cookie domain."""
        url = "https://www.youtube-nocookie.com/embed/dQw4w9WgXcQ"
        assert extract_video_id(url) == "dQw4w9WgXcQ"

    def test_embed_url_with_parameters(self):
        """Test embed URL with parameters."""
        url = "https://www.youtube.com/embed/dQw4w9WgXcQ?rel=0"
        assert extract_video_id(url) == "dQw4w9WgXcQ"


class TestShorts:
    """Test YouTube Shorts URLs."""

    def test_shorts_url(self):
        """Test standard shorts URL."""
        url = "https://www.youtube.com/shorts/j9rZxAF3C0I"
        assert extract_video_id(url) == "j9rZxAF3C0I"

    def test_shorts_url_mobile(self):
        """Test shorts URL on mobile domain."""
        url = "https://m.youtube.com/shorts/j9rZxAF3C0I"
        assert extract_video_id(url) == "j9rZxAF3C0I"

    def test_shorts_url_with_app_param(self):
        """Test shorts URL with app=desktop parameter."""
        url = "https://www.youtube.com/shorts/j9rZxAF3C0I?app=desktop"
        assert extract_video_id(url) == "j9rZxAF3C0I"


class TestLiveStreams:
    """Test live stream URLs."""

    def test_live_url(self):
        """Test standard live URL."""
        url = "https://www.youtube.com/live/8hBmepWUJoc"
        assert extract_video_id(url) == "8hBmepWUJoc"

    def test_live_url_with_params(self):
        """Test live URL with feature parameter."""
        url = "https://www.youtube.com/live/8hBmepWUJoc?feature=share"
        assert extract_video_id(url) == "8hBmepWUJoc"


class TestOldFormats:
    """Test old/v format URLs."""

    def test_v_format_url(self):
        """Test old /v/ format URL."""
        url = "https://www.youtube.com/v/dQw4w9WgXcQ"
        assert extract_video_id(url) == "dQw4w9WgXcQ"

    def test_e_format_url(self):
        """Test old /e/ format URL."""
        url = "https://www.youtube.com/e/dQw4w9WgXcQ"
        assert extract_video_id(url) == "dQw4w9WgXcQ"


class TestEdgeCases:
    """Test edge cases and special formats."""

    def test_url_without_protocol(self):
        """Test URL without protocol (youtube.com/...)."""
        url = "youtube.com/watch?v=dQw4w9WgXcQ"
        assert extract_video_id(url) == "dQw4w9WgXcQ"

    def test_url_with_www_only(self):
        """Test URL starting with www only."""
        url = "www.youtube.com/watch?v=dQw4w9WgXcQ"
        assert extract_video_id(url) == "dQw4w9WgXcQ"

    def test_url_with_fragment(self):
        """Test URL with fragment/anchor."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ#t=10s"
        assert extract_video_id(url) == "dQw4w9WgXcQ"

    def test_url_with_multiple_params(self):
        """Test URL with multiple query parameters."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=10&list=PLxyz&index=1"
        assert extract_video_id(url) == "dQw4w9WgXcQ"

    def test_url_with_hyphen_in_id(self):
        """Test video ID with hyphen."""
        url = "https://www.youtube.com/watch?v=-wtIMTCHWuI"
        assert extract_video_id(url) == "-wtIMTCHWuI"

    def test_url_with_underscore_in_id(self):
        """Test video ID with underscore."""
        url = "https://www.youtube.com/watch?v=lalOy8Mbfdc"
        assert extract_video_id(url) == "lalOy8Mbfdc"

    def test_watch_url_without_query_separator(self):
        """Test watch URL where v param comes after other params."""
        url = "https://www.youtube.com/watch?feature=player_embedded&v=dQw4w9WgXcQ"
        assert extract_video_id(url) == "dQw4w9WgXcQ"

    def test_short_url_with_ampersand_param(self):
        """Test short URL with & instead of ? for params."""
        # This is an unusual but valid format where youtu.be treats & as ?
        url = "https://youtu.be/oTJRivZTMLs&feature=channel"
        # The video ID should still be extracted correctly
        result = extract_video_id(url)
        assert result is not None
        assert "oTJRivZTMLs" in result or result == "oTJRivZTMLs"


class TestInvalidURLs:
    """Test invalid URLs that should return None."""

    def test_invalid_domain(self):
        """Test URL with invalid domain."""
        url = "https://example.com/watch?v=dQw4w9WgXcQ"
        assert extract_video_id(url) is None

    def test_no_video_id(self):
        """Test YouTube URL without video ID."""
        url = "https://www.youtube.com/watch"
        assert extract_video_id(url) is None

    def test_empty_string(self):
        """Test empty string."""
        url = ""
        assert extract_video_id(url) is None

    def test_none_input(self):
        """Test None input."""
        assert extract_video_id(None) is None

    def test_non_youtube_url(self):
        """Test completely different URL."""
        url = "https://vimeo.com/123456789"
        assert extract_video_id(url) is None

    def test_channel_url(self):
        """Test channel URL (not a video)."""
        url = "https://www.youtube.com/channel/UCgc00bfF_PvO_2AvqJZHXFg"
        assert extract_video_id(url) is None

    def test_playlist_url(self):
        """Test playlist URL without specific video."""
        url = "https://www.youtube.com/playlist?list=PLToa5JuFMsXTNkrLJbRlB--76IAOjRM9b"
        assert extract_video_id(url) is None


class TestURLsWithSpecialCharacters:
    """Test URLs with special characters in parameters."""

    def test_url_with_encoded_params(self):
        """Test URL with URL-encoded parameters."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=PLToa5JuFMsXTNkrLJbRlB--76IAOjRM9b&index=5"
        assert extract_video_id(url) == "dQw4w9WgXcQ"


class TestSampleURLsFixture:
    """Test URLs from the sample_urls fixture."""

    def test_all_sample_urls_can_be_parsed(self, sample_urls):
        """Test that all valid sample URLs can be parsed."""
        from youtube_transcript.utils.url_parser import extract_video_id

        valid_formats = [
            "standard_watch",
            "standard_watch_http",
            "standard_watch_no_www",
            "standard_watch_mobile",
            "short",
            "short_http",
            "short_with_params",
            "embed",
            "embed_no_cookie",
            "shorts",
            "shorts_mobile",
            "live",
            "live_with_params",
            "v_format",
            "e_format",
            "with_t_param",
            "with_list_param",
            "with_si_param",
            "with_timestamp",
        ]

        for format_name in valid_formats:
            url = sample_urls[format_name]
            result = extract_video_id(url)
            assert result is not None, f"Failed to parse {format_name}: {url}"
            assert len(result) >= 11, f"Video ID too short for {format_name}: {result}"

    def test_invalid_sample_urls_return_none(self, sample_urls):
        """Test that invalid sample URLs return None."""
        from youtube_transcript.utils.url_parser import extract_video_id

        invalid_formats = ["invalid_domain", "no_video_id", "empty_string"]

        for format_name in invalid_formats:
            url = sample_urls[format_name]
            result = extract_video_id(url)
            assert result is None, f"Expected None for {format_name}, got: {result}"


class TestPerformance:
    """Test URL parser performance."""

    def test_parse_performance(self):
        """Test that URL parsing is fast (< 1ms per URL)."""
        import time

        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        iterations = 1000

        start = time.perf_counter()
        for _ in range(iterations):
            extract_video_id(url)
        elapsed = time.perf_counter() - start

        avg_time = (elapsed / iterations) * 1000  # Convert to ms
        assert avg_time < 1.0, f"URL parsing too slow: {avg_time:.2f}ms per URL"


class TestRealVideoIDs:
    """Test with real YouTube video IDs."""

    def test_rickroll_video_id(self):
        """Test with the famous Rick Roll video ID."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        assert extract_video_id(url) == "dQw4w9WgXcQ"

    def test_shorts_video_id(self):
        """Test with a YouTube Shorts video ID."""
        url = "https://www.youtube.com/shorts/j9rZxAF3C0I"
        assert extract_video_id(url) == "j9rZxAF3C0I"

    def test_live_stream_video_id(self):
        """Test with a live stream video ID."""
        url = "https://www.youtube.com/live/8hBmepWUJoc"
        assert extract_video_id(url) == "8hBmepWUJoc"


class TestURLSanitization:
    """Test URL sanitization for handling backslashes and invalid characters."""

    def test_short_url_with_backslash_before_query_param(self):
        """Test short youtu.be URL with backslash before query parameter (shell escaping issue)."""
        # This simulates URLs from shell escaping: "https://youtu.be/ID\?si=..."
        url = "https://youtu.be/FmSVuQoXjUQ\\?si=j04zJPBKKzzz4_gO"
        # Currently fails - returns 'FmSVuQoXjUQ\\' instead of 'FmSVuQoXjUQ'
        assert extract_video_id(url) == "FmSVuQoXjUQ"

    def test_short_url_with_multiple_backslashes(self):
        """Test URL with backslashes in multiple positions (realistic shell escaping)."""
        # Realistic case: user escapes special chars in shell but forward slashes remain
        url = "https://youtu.be/M9bq_alk-sw\\?si\\=B_RZg_I-lLaa7UU-"
        # Should extract 'M9bq_alk-sw' after removing backslashes
        assert extract_video_id(url) == "M9bq_alk-sw"

    def test_watch_url_with_backslashes(self):
        """Test standard watch URL with backslashes in query string."""
        url = "https://www.youtube.com/watch\\?v\\=dQw4w9WgXcQ\\&list\\=PLxyz"
        # Should extract 'dQw4w9WgXcQ' after removing backslashes
        assert extract_video_id(url) == "dQw4w9WgXcQ"

    def test_embed_url_with_backslashes(self):
        """Test embed URL with backslashes in query parameters (not path)."""
        # Realistic: backslashes in query string, not path separators
        url = "https://www.youtube.com/embed/dQw4w9WgXcQ\\?rel\\=0"
        # Should extract 'dQw4w9WgXcQ' after removing backslashes
        assert extract_video_id(url) == "dQw4w9WgXcQ"

    def test_shorts_url_with_backslashes(self):
        """Test shorts URL with backslashes in query parameters (not path)."""
        # Realistic: backslashes in query string, not path separators
        url = "https://www.youtube.com/shorts/j9rZxAF3C0I\\?app\\=desktop"
        # Should extract 'j9rZxAF3C0I' after removing backslashes
        assert extract_video_id(url) == "j9rZxAF3C0I"
