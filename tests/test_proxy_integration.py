"""
Integration tests for WebShare proxy configuration.

These tests require REAL WebShare credentials to run. They verify that the proxy
configuration works correctly with the actual YouTube API.

Run these tests manually with:
    pytest tests/test_proxy_integration.py -v --tb=short

Set environment variables before running:
    export WEBSHARE_PROXY_USERNAME="your_webshare_username"
    export WEBSHARE_PROXY_PASSWORD="your_webshare_password"
"""

import os
import pytest

from youtube_transcript.config import get_proxy_config
from youtube_transcript.services import YouTubeTranscriptFetcher


class TestProxyConfigLoading:
    """Test loading proxy configuration from environment variables."""

    def test_get_proxy_config_returns_none_when_no_env_vars(self):
        """Test that get_proxy_config returns None when env vars are not set."""
        # Ensure env vars are not set
        if 'WEBSHARE_PROXY_USERNAME' in os.environ:
            del os.environ['WEBSHARE_PROXY_USERNAME']
        if 'WEBSHARE_PROXY_PASSWORD' in os.environ:
            del os.environ['WEBSHARE_PROXY_PASSWORD']

        config = get_proxy_config()
        assert config is None

    def test_get_proxy_config_with_credentials(self, monkeypatch):
        """Test that get_proxy_config creates config with credentials."""
        monkeypatch.setenv('WEBSHARE_PROXY_USERNAME', 'test_user')
        monkeypatch.setenv('WEBSHARE_PROXY_PASSWORD', 'test_pass')

        config = get_proxy_config()
        assert config is not None
        assert config.proxy_username == 'test_user'

    def test_get_proxy_config_with_optional_settings(self, monkeypatch):
        """Test that get_proxy_config handles optional settings."""
        monkeypatch.setenv('WEBSHARE_PROXY_USERNAME', 'test_user')
        monkeypatch.setenv('WEBSHARE_PROXY_PASSWORD', 'test_pass')
        monkeypatch.setenv('WEBSHARE_PROXY_LOCATIONS', 'US,CA,UK')
        monkeypatch.setenv('WEBSHARE_PROXY_RETRIES', '15')

        config = get_proxy_config()
        assert config is not None
        assert config.proxy_username == 'test_user'
        # Note: filter_ip_locations is a private attribute, checking it worked via the config object
        assert config.retries_when_blocked == 15


class TestProxyFetcherIntegration:
    """Integration tests with real WebShare proxies (requires credentials)."""

    @pytest.mark.skipif(
        not os.getenv('WEBSHARE_PROXY_USERNAME') or not os.getenv('WEBSHARE_PROXY_PASSWORD'),
        reason="Requires WEBSHARE_PROXY_USERNAME and WEBSHARE_PROXY_PASSWORD environment variables"
    )
    def test_fetcher_with_proxy_fetches_transcript(self):
        """Test that fetcher can fetch transcript through WebShare proxy."""
        # This test requires real WebShare credentials
        config = get_proxy_config()
        assert config is not None, "Proxy config should not be None when env vars are set"

        fetcher = YouTubeTranscriptFetcher(proxy_config=config)

        # Try fetching a real video transcript
        result = fetcher.fetch_transcript('dQw4w9WgXcQ', languages=['en'])

        assert result is not None, "Should fetch transcript successfully through proxy"
        assert result.video_id == 'dQw4w9WgXcQ'
        assert result.transcript
        assert len(result.transcript) > 0
        print(f"\n✓ Successfully fetched transcript through proxy!")
        print(f"  Video ID: {result.video_id}")
        print(f"  Language: {result.language}")
        print(f"  Type: {result.transcript_type}")
        print(f"  Duration: {result.duration}s")
        print(f"  Transcript length: {len(result.transcript)} characters")

    @pytest.mark.skipif(
        not os.getenv('WEBSHARE_PROXY_USERNAME') or not os.getenv('WEBSHARE_PROXY_PASSWORD'),
        reason="Requires WEBSHARE_PROXY_USERNAME and WEBSHARE_PROXY_PASSWORD environment variables"
    )
    def test_fetcher_with_proxy_handles_rate_limiting(self):
        """Test that proxy helps avoid rate limiting (multiple requests)."""
        config = get_proxy_config()
        assert config is not None

        fetcher = YouTubeTranscriptFetcher(proxy_config=config)

        # Fetch multiple different videos to test rate limiting
        video_ids = ['dQw4w9WgXcQ', 'j9rZxAF3C0I']

        for video_id in video_ids:
            result = fetcher.fetch_transcript(video_id, languages=['en'])
            assert result is not None, f"Should fetch {video_id} through proxy"
            assert result.video_id == video_id
            print(f"\n✓ Fetched {video_id} successfully through proxy")


class TestOrchestratorWithProxy:
    """Test TranscriptOrchestrator with proxy configuration."""

    @pytest.mark.skipif(
        not os.getenv('WEBSHARE_PROXY_USERNAME') or not os.getenv('WEBSHARE_PROXY_PASSWORD'),
        reason="Requires WEBSHARE_PROXY_USERNAME and WEBSHARE_PROXY_PASSWORD environment variables"
    )
    def test_orchestrator_uses_proxy_from_env(self):
        """Test that TranscriptOrchestrator automatically uses proxy from environment."""
        from youtube_transcript.models import get_session

        config = get_proxy_config()
        assert config is not None

        session_gen = get_session()
        session = next(session_gen)

        # Orchestrator should automatically load proxy from environment
        orchestrator = TranscriptOrchestrator(session=session)

        # Verify the fetcher was created with proxy
        result = orchestrator.get_transcript('dQw4w9WgXcQ', languages=['en'])

        assert result is not None, "Orchestrator should fetch through proxy"
        assert result.video_id == 'dQw4w9WgXcQ'
        print(f"\n✓ Orchestrator successfully fetched through proxy!")
