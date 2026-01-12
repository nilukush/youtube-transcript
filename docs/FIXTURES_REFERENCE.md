# Testing Fixtures Quick Reference

## Overview

This document provides a quick reference for all available pytest fixtures
in the YouTube Transcript Fetcher project.

## Core Fixtures

### test_db (function scope)

In-memory SQLite database for testing.

```python
def test_example(test_db):
    # test_db is a SQLModel Session
    from youtube_transcript.models import Transcript
    
    transcript = Transcript(video_id="abc", transcript_text="Hello")
    test_db.add(transcript)
    test_db.commit()
    
    result = test_db.query(Transcript).first()
    assert result.video_id == "abc"
```

### mock_redis (function scope)

Fake Redis client using fakeredis.

```python
def test_example(mock_redis):
    # Supports all Redis operations
    mock_redis.set("key", "value")
    assert mock_redis.get("key") == b"value"
    assert mock_redis.exists("key") == 1
    
    mock_redis.delete("key")
    assert mock_redis.exists("key") == 0
```

### sample_urls (session scope)

Dictionary of 20+ YouTube URL formats.

```python
def test_example(sample_urls):
    # Access specific URL formats
    standard_url = sample_urls["standard_watch"]
    short_url = sample_urls["short"]
    shorts_url = sample_urls["shorts"]
    
    # Iterate all URLs
    for name, url in sample_urls.items():
        print(f"{name}: {url}")
```

### sample_video_ids (session scope)

Dictionary of test video IDs.

```python
def test_example(sample_video_ids):
    rickroll_id = sample_video_ids["rickroll"]
    # Result: "dQw4w9WgXcQ"
    
    shorts_id = sample_video_ids["shorts"]
    # Result: "j9rZxAF3C0I"
```

### test_client (function scope)

FastAPI test client (stub until Step 9).

```python
def test_example(test_client):
    # Will be implemented in Step 9
    # For now, returns None
    pass
```

## Utility Fixtures

### sample_transcript_data (function scope)

Sample transcript structure for testing.

```python
def test_example(sample_transcript_data):
    # Access transcript fields
    video_id = sample_transcript_data["video_id"]
    text = sample_transcript_data["text"]
    language = sample_transcript_data["language"]
    segments = sample_transcript_data["segments"]
    
    # Use in tests
    assert len(text) > 0
    assert language == "en"
    assert len(segments) == 3
```

### test_cache_key_prefix (session scope)

Consistent cache key prefix for tests.

```python
def test_example(mock_redis, test_cache_key_prefix):
    # Build cache key
    cache_key = f"{test_cache_key_prefix}:video:abc123"
    # Result: "ytt:test:video:abc123"
    
    mock_redis.set(cache_key, "transcript_data")
    assert mock_redis.get(cache_key) == b"transcript_data"
```

### test_environment (session scope, auto-used)

Automatically sets test environment variables.

```python
def test_example():
    import os
    
    # Environment is already set
    assert os.environ["ENVIRONMENT"] == "test"
    assert os.environ["LOG_LEVEL"] == "DEBUG"
```

## Sample URL Categories

### Standard Watch URLs
- `standard_watch`: https://www.youtube.com/watch?v=dQw4w9WgXcQ
- `standard_watch_http`: http://www.youtube.com/watch?v=dQw4w9WgXcQ
- `standard_watch_no_www`: https://youtube.com/watch?v=dQw4w9WgXcQ
- `standard_watch_mobile`: https://m.youtube.com/watch?v=dQw4w9WgXcQ

### Short URLs (youtu.be)
- `short`: https://youtu.be/dQw4w9WgXcQ
- `short_http`: http://youtu.be/dQw4w9WgXcQ
- `short_with_params`: https://youtu.be/dQw4w9WgXcQ?t=10

### Embed URLs
- `embed`: https://www.youtube.com/embed/dQw4w9WgXcQ
- `embed_no_cookie`: https://www.youtube-nocookie.com/embed/dQw4w9WgXcQ

### YouTube Shorts
- `shorts`: https://www.youtube.com/shorts/j9rZxAF3C0I
- `shorts_mobile`: https://m.youtube.com/shorts/j9rZxAF3C0I

### Live Streams
- `live`: https://www.youtube.com/live/8hBmepWUJoc
- `live_with_params`: https://www.youtube.com/live/8hBmepWUJoc?feature=share

### With Parameters
- `with_t_param`: https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=10s
- `with_list_param`: https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=PLxyz123
- `with_si_param`: https://youtu.be/dQw4w9WgXcQ?si=B_RZg_I-lLaa7UU-

### Invalid URLs (for error testing)
- `invalid_domain`: https://example.com/watch?v=dQw4w9WgXcQ
- `no_video_id`: https://www.youtube.com/watch
- `empty_string`: ""

## Fixture Scopes

- **function**: Fresh fixture for each test function (default)
- **session**: Created once per test session, shared across tests

## Using Multiple Fixtures

```python
def test_complex_scenario(test_db, mock_redis, sample_urls):
    # Use database
    transcript = Transcript(video_id="abc")
    test_db.add(transcript)
    
    # Use cache
    mock_redis.set("cache_key", "cached_value")
    
    # Use sample data
    url = sample_urls["standard_watch"]
    
    # Test interaction between components
    assert True
```

## Best Practices

1. **Use descriptive test names** that indicate what is being tested
2. **One assertion per test** when possible
3. **Arrange-Act-Assert (AAA) pattern**:
   ```python
   def test_something(test_db):
       # Arrange: Set up data
       transcript = Transcript(video_id="abc")
       test_db.add(transcript)
       test_db.commit()
       
       # Act: Perform action
       result = test_db.query(Transcript).first()
       
       # Assert: Verify result
       assert result.video_id == "abc"
   ```

4. **Use appropriate fixtures** for the test scope
5. **Don't worry about cleanup** - fixtures handle it automatically

## Discovering Fixtures

To see all available fixtures:

```bash
pytest --fixtures tests/
```

To see fixtures used by a specific test:

```bash
pytest --fixtures tests/test_specific_file.py
```

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_fixture_functionality.py -v

# Run specific test
pytest tests/test_fixture_functionality.py::test_mock_redis_operations -v

# Run with coverage
pytest tests/ --cov=src/youtube_transcript --cov-report=html
```
