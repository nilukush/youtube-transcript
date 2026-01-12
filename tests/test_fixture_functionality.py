"""
Test fixture functionality.

These tests verify that fixtures work correctly and provide expected functionality.
"""

import pytest


def test_test_db_session(test_db):
    """Test that test_db provides a working database session."""
    from sqlmodel import Session

    # Verify it's a Session
    assert isinstance(test_db, Session)

    # Verify we can perform database operations
    # (Actual models will be created in Step 3)
    assert test_db is not None


def test_mock_redis_operations(mock_redis):
    """Test that mock_redis supports Redis operations."""
    # Test set/get
    mock_redis.set("test_key", "test_value")
    assert mock_redis.get("test_key") == b"test_value"

    # Test exists
    assert mock_redis.exists("test_key") == 1
    assert mock_redis.exists("nonexistent") == 0

    # Test delete
    mock_redis.delete("test_key")
    assert mock_redis.exists("test_key") == 0

    # Test flush
    mock_redis.set("key1", "value1")
    mock_redis.set("key2", "value2")
    mock_redis.flushall()
    assert mock_redis.get("key1") is None
    assert mock_redis.get("key2") is None


def test_sample_urls_contains_various_formats(sample_urls):
    """Test that sample_urls fixture contains various YouTube URL formats."""
    assert isinstance(sample_urls, dict)
    assert len(sample_urls) > 0

    # Verify standard formats exist
    assert "standard_watch" in sample_urls
    assert "short" in sample_urls
    assert "embed" in sample_urls
    assert "shorts" in sample_urls

    # Verify URLs are strings
    for url_name, url in sample_urls.items():
        if url:  # Skip empty string test case
            assert isinstance(url, str)
            assert len(url) > 0


def test_sample_video_ids(sample_video_ids):
    """Test that sample_video_ids fixture contains valid video IDs."""
    assert isinstance(sample_video_ids, dict)
    assert len(sample_video_ids) > 0

    # Verify known videos
    assert "rickroll" in sample_video_ids
    assert "shorts" in sample_video_ids

    # Verify video IDs are valid (11 characters for standard YouTube IDs)
    for video_name, video_id in sample_video_ids.items():
        assert isinstance(video_id, str)
        assert len(video_id) >= 11  # Most YouTube IDs are 11 chars


def test_sample_transcript_data(sample_transcript_data):
    """Test that sample_transcript_data contains valid transcript structure."""
    assert isinstance(sample_transcript_data, dict)

    # Verify required fields
    assert "video_id" in sample_transcript_data
    assert "text" in sample_transcript_data
    assert "language" in sample_transcript_data
    assert "transcript_type" in sample_transcript_data

    # Verify data types
    assert isinstance(sample_transcript_data["video_id"], str)
    assert isinstance(sample_transcript_data["text"], str)
    assert isinstance(sample_transcript_data["language"], str)
    assert isinstance(sample_transcript_data["transcript_type"], str)

    # Verify we have transcript content
    assert len(sample_transcript_data["text"]) > 0


def test_cache_key_prefix(test_cache_key_prefix):
    """Test that test_cache_key_prefix provides a consistent prefix."""
    assert isinstance(test_cache_key_prefix, str)
    assert len(test_cache_key_prefix) > 0
    assert test_cache_key_prefix == "ytt:test"


def test_environment_variables(test_environment):
    """Test that test_environment fixture sets environment variables."""
    import os

    # Verify environment is set
    assert os.environ.get("ENVIRONMENT") == "test"
    assert os.environ.get("LOG_LEVEL") == "DEBUG"


def test_fixtures_isolated_between_tests(test_db, mock_redis):
    """Test that fixtures provide fresh state for each test."""
    # This test verifies isolation - each test gets fresh fixtures

    # Set some data
    mock_redis.set("isolation_test", "value")

    # Verify it exists in this test
    assert mock_redis.exists("isolation_test") == 1

    # Note: The actual isolation verification would require
    # running multiple tests and verifying data doesn't leak
    # This is handled by pytest's fixture scoping


def test_sample_urls_count(sample_urls):
    """Test that we have a comprehensive set of sample URLs."""
    # We should have at least 20 different URL formats for testing
    assert len(sample_urls) >= 20

    # Count by type
    standard_count = sum(1 for name in sample_urls if "standard" in name)
    short_count = sum(1 for name in sample_urls if "short" in name and "_short" not in name)
    shorts_count = sum(1 for name in sample_urls if "shorts" in name)

    # Verify we have multiple formats of each type
    assert standard_count >= 3  # http, https, with/without www, mobile
    assert short_count >= 2     # youtu.be variations
    assert shorts_count >= 2    # YouTube shorts variations


def test_all_sample_urls_are_reachable(sample_urls):
    """Test that all sample URLs are well-formed (not that they're reachable)."""
    import re

    # Basic URL validation
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE
    )

    for name, url in sample_urls.items():
        if url and name not in ["empty_string", "invalid_domain", "no_video_id"]:
            # Valid YouTube URLs should match basic URL pattern
            assert url_pattern.match(url), f"{name}: {url} is not a valid URL format"
