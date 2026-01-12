"""
Pytest configuration and shared fixtures.

This module contains all shared fixtures used across the test suite.
Fixtures are automatically discovered by pytest.
"""

import pytest
from typing import Dict
from sqlmodel import SQLModel, create_engine, Session
from fakeredis import FakeStrictRedis


# =============================================================================
# Database Fixtures
# =============================================================================

@pytest.fixture(scope="function")
def test_db():
    """
    Provide an in-memory SQLite database for testing.

    This fixture creates a fresh in-memory database for each test function.
    All tables are created automatically at the start of each test.

    Yields:
        Session: SQLModel Session for database operations

    Example:
        def test_something(test_db):
            transcript = Transcript(video_id="abc", transcript_text="Hello")
            test_db.add(transcript)
            test_db.commit()
    """
    # Import here to avoid circular imports
    from sqlmodel import SQLModel

    # Create in-memory SQLite engine
    engine = create_engine("sqlite:///:memory:")

    # Create all tables
    SQLModel.metadata.create_all(engine)

    # Create session
    session = Session(engine)

    yield session

    # Cleanup: close session and dispose engine
    session.close()
    engine.dispose()


# =============================================================================
# Redis Fixtures
# =============================================================================

@pytest.fixture(scope="function")
def mock_redis():
    """
    Provide a fake Redis client for testing.

    This fixture uses fakeredis to mimic Redis behavior without requiring
    a real Redis server. All data is stored in-memory and discarded after
    each test.

    Yields:
        FakeStrictRedis: A fake Redis client that behaves like redis.Redis

    Example:
        def test_cache(mock_redis):
            mock_redis.set("key", "value")
            assert mock_redis.get("key") == b"value"
    """
    # Create fake Redis client
    redis_client = FakeStrictRedis(decode_responses=False)

    yield redis_client

    # Cleanup: flush all data
    redis_client.flushall()


# =============================================================================
# Sample Data Fixtures
# =============================================================================

@pytest.fixture(scope="session")
def sample_urls() -> Dict[str, str]:
    """
    Provide sample YouTube URLs for testing.

    This fixture contains a dictionary of various YouTube URL formats
    to test URL parsing and video ID extraction.

    Returns:
        Dict[str, str]: Dictionary mapping URL format names to URLs

    Example:
        def test_url_parsing(sample_urls):
            url = sample_urls["standard_watch"]
            video_id = extract_video_id(url)
            assert video_id == "dQw4w9WgXcQ"
    """
    return {
        # Standard watch URLs
        "standard_watch": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "standard_watch_http": "http://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "standard_watch_no_www": "https://youtube.com/watch?v=dQw4w9WgXcQ",
        "standard_watch_mobile": "https://m.youtube.com/watch?v=dQw4w9WgXcQ",

        # Short URLs (youtu.be)
        "short": "https://youtu.be/dQw4w9WgXcQ",
        "short_http": "http://youtu.be/dQw4w9WgXcQ",
        "short_with_params": "https://youtu.be/dQw4w9WgXcQ?t=10",

        # Embed URLs
        "embed": "https://www.youtube.com/embed/dQw4w9WgXcQ",
        "embed_no_cookie": "https://www.youtube-nocookie.com/embed/dQw4w9WgXcQ",

        # Shorts
        "shorts": "https://www.youtube.com/shorts/j9rZxAF3C0I",
        "shorts_mobile": "https://m.youtube.com/shorts/j9rZxAF3C0I",

        # Live streams
        "live": "https://www.youtube.com/live/8hBmepWUJoc",
        "live_with_params": "https://www.youtube.com/live/8hBmepWUJoc?feature=share",

        # Old embed format
        "v_format": "https://www.youtube.com/v/dQw4w9WgXcQ",
        "e_format": "https://www.youtube.com/e/dQw4w9WgXcQ",

        # With query parameters
        "with_t_param": "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=10s",
        "with_list_param": "https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=PLxyz123",
        "with_si_param": "https://youtu.be/dQw4w9WgXcQ?si=B_RZg_I-lLaa7UU-",

        # With timestamps
        "with_timestamp": "https://www.youtube.com/watch?v=dQw4w9WgXcQ#t=10s",

        # Invalid URLs (for testing error handling)
        "invalid_domain": "https://example.com/watch?v=dQw4w9WgXcQ",
        "no_video_id": "https://www.youtube.com/watch",
        "empty_string": "",
    }


@pytest.fixture(scope="session")
def sample_video_ids() -> Dict[str, str]:
    """
    Provide sample video IDs for testing.

    Returns:
        Dict[str, str]: Dictionary mapping video names to video IDs

    Example:
        def test_transcript_fetch(sample_video_ids):
            video_id = sample_video_ids["rickroll"]
            transcript = fetcher.fetch(video_id)
    """
    return {
        # Real video IDs (these should have transcripts)
        "rickroll": "dQw4w9WgXcQ",  # Rick Astley - Never Gonna Give You Up
        "shorts": "j9rZxAF3C0I",     # YouTube Short
        "live": "8hBmepWUJoc",       # Live stream

        # Test video IDs (for edge cases)
        "with_hyphen": "-wtIMTCHWuI",
        "with_underscore": "lalOy8Mbfdc",
    }


# =============================================================================
# FastAPI Test Client Fixture
# =============================================================================

@pytest.fixture(scope="function")
def test_client():
    """
    Provide a FastAPI test client for testing API endpoints.

    This fixture creates a test client that can make requests to FastAPI
    endpoints without running a server.

    Yields:
        TestClient: Starlette TestClient for making HTTP requests

    Example:
        def test_api_endpoint(test_client):
            response = test_client.post("/api/transcript", json={"url": "..."})
            assert response.status_code == 200
    """
    from fastapi.testclient import TestClient
    from youtube_transcript.api.app import app

    client = TestClient(app)
    yield client


# =============================================================================
# Environment Fixture
# =============================================================================

@pytest.fixture(scope="session", autouse=True)
def test_environment():
    """
    Set up test environment variables.

    This fixture runs automatically for all tests and sets environment
    variables to ensure tests run in a consistent environment.
    """
    import os

    # Set test environment
    os.environ["ENVIRONMENT"] = "test"
    os.environ["LOG_LEVEL"] = "DEBUG"

    yield

    # Cleanup: remove environment variables
    os.environ.pop("ENVIRONMENT", None)
    os.environ.pop("LOG_LEVEL", None)


# =============================================================================
# Utility Fixtures
# =============================================================================

@pytest.fixture(scope="session")
def test_cache_key_prefix() -> str:
    """
    Provide a prefix for test cache keys.

    Returns:
        str: Prefix to use for all cache keys in tests

    Example:
        def test_caching(mock_redis, test_cache_key_prefix):
            key = f"{test_cache_key_prefix}:video:abc123"
            mock_redis.set(key, "value")
    """
    return "ytt:test"


@pytest.fixture(scope="function")
def sample_transcript_data():
    """
    Provide sample transcript data for testing.

    Returns:
        dict: Sample transcript data structure

    Example:
        def test_transcript_processing(sample_transcript_data):
            text = sample_transcript_data["text"]
            assert len(text) > 0
    """
    return {
        "video_id": "dQw4w9WgXcQ",
        "text": "Never gonna give you up\nNever gonna let you down\nNever gonna run around and desert you",
        "language": "en",
        "transcript_type": "manual",
        "duration": 212,
        "segments": [
            {"text": "Never gonna give you up", "start": 0.0, "duration": 3.5},
            {"text": "Never gonna let you down", "start": 3.5, "duration": 3.2},
            {"text": "Never gonna run around and desert you", "start": 6.7, "duration": 4.1},
        ],
    }
