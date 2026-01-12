# YouTube Transcript Fetcher - Detailed Implementation Plan

**Date**: January 11, 2026
**Document Version**: 1.0
**Status**: Ready for Execution
**Based on**: Analysis in `docs/ANALYSIS.md`

---

## Phase 0: Project Setup and Infrastructure

---

### Step 1: Initialize Project Structure

**Objective**: Set up the foundational project structure with Python packaging, virtual environment, and development tools.

**Prerequisites**: None (first step)

**Test First**:
```
Test type: Integration
Test cases:
  ✓ Test that project structure is valid (pyproject.toml exists)
  ✓ Test that Python package can be imported
  ✓ Test that CLI entry point is registered
  ✓ Test that basic imports work (fastapi, typer, sqlmodel)
Expected: All tests fail because package doesn't exist yet
```

**Implementation**:
- Create `pyproject.toml` with project metadata
- Set up `src/` directory structure
- Configure development dependencies (pytest, black, ruff, mypy)
- Create basic `__init__.py` files
- Set up virtual environment

**Acceptance Criteria**:
- ✓ `pip install -e .` succeeds
- ✓ `python -c "import youtube_transcript"` succeeds
- ✓ `ytt --help` shows CLI help (even if minimal)
- ✓ `pytest` discovers test directory
- ✓ Development tools (black, ruff, mypy) configured

**Verification**:
```bash
# Verify package can be installed
pip install -e .

# Verify CLI is registered
ytt --help

# Verify imports work
python -c "import youtube_transcript"

# Run tests
pytest tests/ -v
```

**Stop/Go Decision**: Proceed to Step 2

---

### Step 2: Set Up Testing Infrastructure

**Objective**: Establish comprehensive testing framework with pytest, fixtures, and CI configuration.

**Prerequisites**: Step 1 complete

**Test First**:
```
Test type: Integration
Test cases:
  ✓ Test that pytest can discover tests
  ✓ Test that fixtures can be loaded
  ✓ Test that test database can be created (in-memory SQLite)
  ✓ Test that Redis mock works
Expected: Tests fail because fixtures don't exist
```

**Implementation**:
- Create `tests/` directory with structure matching `src/`
- Set up `conftest.py` with shared fixtures:
  - `test_db`: In-memory SQLite database
  - `test_client`: FastAPI test client
  - `mock_redis`: Mock Redis client
  - `sample_youtube_urls`: Fixture with test URLs
- Configure pytest (`pytest.ini`, `pyproject.toml`)
- Set up coverage reporting (`pytest-cov`)
- Create GitHub Actions CI workflow (optional)

**Scope**: Minimal infrastructure to enable TDD

**Constraints**:
- Use pytest fixtures extensively
- Tests must be isolated (no shared state)
- Use `pytest-asyncio` for async tests
- Target 80%+ coverage from the start

**Acceptance Criteria**:
- ✓ `pytest tests/ -v` runs without errors (even with 0 tests initially)
- ✓ `pytest --cov=youtube_transcript` reports coverage
- ✓ `conftest.py` contains at least 3 useful fixtures
- ✓ CI pipeline runs tests on push (if GitHub)

**Verification**:
```bash
# Run tests
pytest tests/ -v

# Run with coverage
pytest --cov=youtube_transcript --cov-report=html

# Verify fixtures
pytest --fixtures
```

**Stop/Go Decision**: Proceed to Step 3

---

### Step 3: Set Up Database Schema and ORM

**Objective**: Define database models using SQLModel and establish migration system.

**Prerequisites**: Step 2 complete

**Test First**:
```
Test type: Unit
Test cases:
  ✓ Test that Transcript model can be created
  ✓ Test that Transcript model fields are correctly typed
  ✓ Test that video_id is unique
  ✓ Test that created_at and updated_at are automatically set
  ✓ Test that transcript text can be stored and retrieved
Expected: Tests fail because models don't exist
```

**Implementation**:
- Create `src/youtube_transcript/models/` directory
- Define `Transcript` model with SQLModel:
  - `id: Optional[int]` (primary key)
  - `video_id: str` (unique, indexed)
  - `transcript_text: str`
  - `language: str` (default: "en")
  - `transcript_type: str` (manual/auto)
  - `created_at: datetime`
  - `updated_at: datetime`
  - `cache_key: str` (for Redis)
- Create database engine singleton
- Implement `init_db()` function
- Add `get_session()` dependency for FastAPI

**Scope**: Just the Transcript model, no queries yet

**Constraints**:
- Use SQLModel (Pydantic + SQLAlchemy)
- All fields must have type hints
- Use `datetime.utcnow()` for timestamps
- Index `video_id` for fast lookups

**Acceptance Criteria**:
- ✓ `Transcript` model has all required fields
- ✓ `video_id` has unique constraint
- ✓ `pytest tests/test_models.py` passes all model tests
- ✓ Database tables can be created successfully
- ✓ Model is Pydantic-compatible (for FastAPI)

**Verification**:
```bash
# Run model tests
pytest tests/test_models.py -v

# Verify table creation
python -c "from youtube_transcript.models import init_db; init_db()"
```

**Stop/Go Decision**: Proceed to Step 4

---

### Step 4: Implement YouTube URL Parser

**Objective**: Create robust URL parser that extracts video IDs from all YouTube URL formats.

**Prerequisites**: Step 3 complete

**Test First**:
```
Test type: Unit
Test cases:
  ✓ Test standard youtube.com/watch?v=ID format
  ✓ Test youtu.be/ID short format
  ✓ Test youtube.com/shorts/ID format
  ✓ Test youtube.com/live/ID format
  ✓ Test youtube.com/embed/ID format
  ✓ Test mobile (m.youtube.com) URLs
  ✓ Test URLs with query parameters (?t=10, ?si=xyz)
  ✓ Test URLs with fragments (#t=10s)
  ✓ Test URLs without protocol (youtube.com/...)
  ✓ Test invalid URLs return None
Expected: Tests fail because parser doesn't exist
```

**Implementation**:
- Create `src/youtube_transcript/utils/` directory
- Implement `extract_video_id(url: str) -> Optional[str]`
- Use regex patterns from the GitHub gist research
- Handle all 100+ URL formats documented
- Return `None` for invalid URLs

**Scope**: URL parsing only, no validation beyond format

**Constraints**:
- Use community-tested regex patterns
- Support all active YouTube URL formats
- Handle edge cases (missing protocol, extra params, etc.)
- Return clean 11-character video ID or None

**Acceptance Criteria**:
- ✓ All test URL formats pass
- ✓ Invalid URLs return None
- ✓ Code coverage > 95% for this module
- ✓ Function is well-documented with examples
- ✓ Performance: < 1ms per URL parse

**Verification**:
```bash
# Run URL parser tests
pytest tests/test_url_parser.py -v

# Test against real URLs
python -c "from youtube_transcript.utils import extract_video_id; print(extract_video_id('https://youtu.be/dQw4w9WgXcQ'))"
# Expected output: dQw4w9WgXcQ
```

**Stop/Go Decision**: Proceed to Step 5

---

## Phase 1: Core Transcript Fetching

---

### Step 5: Implement YouTube Transcript Fetcher (with youtube-transcript-api)

**Objective**: Create service layer to fetch transcripts from YouTube using the youtube-transcript-api library.

**Prerequisites**: Step 4 complete

**Test First**:
```
Test type: Integration (with mocked YouTube)
Test cases:
  ✓ Test fetching transcript from real video (with mocked API)
  ✓ Test that transcript text is returned correctly
  ✓ Test that language preference is respected
  ✓ Test handling of videos without transcripts
  ✓ Test handling of private/deleted videos
  ✓ Test handling of rate limits
  ✓ Test that transcript metadata is captured
Expected: Tests fail because fetcher doesn't exist
```

**Implementation**:
- Create `src/youtube_transcript/services/` directory
- Implement `YouTubeTranscriptFetcher` class:
  - `fetch_transcript(video_id: str, languages: List[str] = None) -> TranscriptResult`
  - Handle `TranscriptsDisabled` exception
  - Handle `VideoUnavailable` exception
  - Parse transcript data into structured format
- Mock `youtube_transcript_api` in tests
- Use `responses` library or `unittest.mock` for HTTP mocking

**Scope**: Fetching only, no caching yet

**Constraints**:
- Must handle all exceptions gracefully
- Return structured data (Pydantic model)
- Support multiple languages
- Preserve timestamps if available
- Never expose raw exceptions to users

**Acceptance Criteria**:
- ✓ Successfully fetches transcript for test video
- ✓ Returns `None` or raises specific error for unavailable transcripts
- ✓ Handles rate limiting with backoff
- ✓ All tests pass with mocked API
- ✓ Can fetch real transcript in manual test

**Verification**:
```bash
# Run fetcher tests
pytest tests/test_fetcher.py -v

# Manual test with real video (optional)
python -c "from youtube_transcript.services import YouTubeTranscriptFetcher; f = YouTubeTranscriptFetcher(); print(f.fetch_transcript('dQw4w9WgXcQ'))"
```

**Stop/Go Decision**: Proceed to Step 6

---

### Step 6: Implement Redis Caching Layer

**Objective**: Add Redis caching to store fetched transcripts and reduce API calls.

**Prerequisites**: Step 5 complete

**Test First**:
```
Test type: Integration (with Redis mock)
Test cases:
  ✓ Test that transcript is cached after first fetch
  ✓ Test that cached transcript is returned on second request
  ✓ Test that cache expires after TTL (7 days)
  ✓ Test that cache can be bypassed with force_refresh flag
  ✓ Test cache key generation
  ✓ Test handling of Redis connection errors
Expected: Tests fail because caching layer doesn't exist
```

**Implementation**:
- Create `src/youtube_transcript/cache/` directory
- Implement `RedisCache` class:
  - `get(key: str) -> Optional[str]`
  - `set(key: str, value: str, ttl: int = 604800)` (7 days)
  - `delete(key: str)`
  - `exists(key: str) -> bool`
- Create cache key from video_id
- Use fakeredis for testing
- Implement graceful degradation (continue without cache if Redis is down)

**Scope**: Caching only, business logic integration comes later

**Constraints**:
- Use Redis with 7-day default TTL
- Graceful degradation if Redis unavailable
- Cache keys must be predictable
- Use JSON serialization for complex objects
- Handle connection errors

**Acceptance Criteria**:
- ✓ First call fetches from YouTube, caches result
- ✓ Second call returns cached result
- ✓ Cache expires after 7 days
- ✓ `force_refresh=True` bypasses cache
- ✓ Tests use fakeredis (no real Redis needed)
- ✓ System works without Redis (degraded mode)

**Verification**:
```bash
# Run cache tests
pytest tests/test_cache.py -v

# Test with real Redis (optional in dev)
docker run -p 6379:6379 -d redis
python -c "from youtube_transcript.cache import RedisCache; c = RedisCache(); c.set('test', 'value'); print(c.get('test'))"
```

**Stop/Go Decision**: Proceed to Step 7

---

### Step 7: Implement Database Persistence

**Objective**: Add database layer to persist transcripts and track usage.

**Prerequisites**: Step 6 complete

**Test First**:
```
Test type: Integration
Test cases:
  ✓ Test that transcript is saved to database after fetch
  ✓ Test that existing transcript is updated (not duplicated)
  ✓ Test retrieval by video_id
  ✓ Test that created_at and updated_at are managed
  ✓ Test uniqueness constraint on video_id
Expected: Tests fail because repository doesn't exist
```

**Implementation**:
- Create `src/youtube_transcript/repository/` directory
- Implement `TranscriptRepository` class:
  - `save(transcript: Transcript) -> Transcript`
  - `get_by_video_id(video_id: str) -> Optional[Transcript]`
  - `exists(video_id: str) -> bool`
  - `update(video_id: str, transcript: str) -> Transcript`
- Use SQLModel for database operations
- Handle race conditions (concurrent saves)

**Scope**: CRUD operations for transcripts only

**Constraints**:
- Use SQLModel sessions
- Handle database errors gracefully
- Use upsert pattern (update if exists, insert if not)
- All methods must be type-hinted

**Acceptance Criteria**:
- ✓ Transcript is saved to database
- ✓ Duplicate video_id updates existing record
- ✓ Retrieval by video_id works
- ✓ Timestamps are managed automatically
- ✓ Database constraints are enforced

**Verification**:
```bash
# Run repository tests
pytest tests/test_repository.py -v

# Verify database persistence
python -c "from youtube_transcript.repository import TranscriptRepository; r = TranscriptRepository(); t = r.get_by_video_id('dQw4w9WgXcQ'); print(t)"
```

**Stop/Go Decision**: Proceed to Step 8

---

### Step 8: Integrate All Layers (Service Orchestrator)

**Objective**: Create unified service that orchestrates fetching, caching, and persistence.

**Prerequisites**: Step 7 complete

**Test First**:
```
Test type: Integration
Test cases:
  ✓ Test first request checks cache miss, fetches from YouTube, saves to DB and cache
  ✓ Test second request checks cache hit, returns cached result
  ✓ Test that cache expiration triggers refetch
  ✓ Test that force_refresh bypasses cache
  ✓ Test graceful handling of YouTube errors
  ✓ Test graceful handling of database errors
  ✓ Test graceful handling of cache errors
Expected: Tests fail because orchestrator doesn't exist
```

**Implementation**:
- Create `src/youtube_transcript/services/transcript_service.py`
- Implement `TranscriptService` class:
  - `get_transcript(video_id: str, force_refresh: bool = False) -> Optional[Transcript]`
  - Flow: Check cache → Check DB → Fetch from YouTube → Save to DB & Cache → Return
  - Handle all error cases
  - Log all operations
- Wire all dependencies (fetcher, cache, repository)

**Scope**: Orchestration only, business logic is in other layers

**Constraints**:
- Cache first (fastest)
- Database second (persistent)
- YouTube fetch third (slowest)
- Graceful degradation at each layer
- Comprehensive logging

**Acceptance Criteria**:
- ✓ First request: cache miss → fetch → save → cache → return
- ✓ Second request: cache hit → return (no fetch)
- ✓ Expired cache: cache miss → DB hit → return
- ✓ `force_refresh=True`: bypasses cache, fetches fresh
- ✓ All error cases handled gracefully
- ✓ End-to-end flow works

**Verification**:
```bash
# Run integration tests
pytest tests/test_transcript_service.py -v

# Manual end-to-end test
python -c "from youtube_transcript.services import TranscriptService; s = TranscriptService(); t = s.get_transcript('dQw4w9WgXcQ'); print(t.transcript_text[:100])"
```

**Stop/Go Decision**: Proceed to Step 9

---

## Phase 2: Web API

---

### Step 9: Implement FastAPI Application Core

**Objective**: Set up FastAPI application with configuration, middleware, and basic structure.

**Prerequisites**: Step 8 complete

**Test First**:
```
Test type: Integration
Test cases:
  ✓ Test that FastAPI app starts successfully
  ✓ Test that CORS middleware is configured
  ✓ Test that health check endpoint returns 200
  ✓ Test that API docs are available at /docs
  ✓ Test that configuration is loaded
Expected: Tests fail because FastAPI app doesn't exist
```

**Implementation**:
- Create `src/youtube_transcript/api/` directory
- Create `main.py` with FastAPI app
- Configure CORS (allow all origins in dev, specific in prod)
- Add health check endpoint: `GET /health`
- Load configuration from environment variables
- Set up middleware (logging, error handling)
- Create API router for transcript endpoints

**Scope**: App structure only, no business endpoints yet

**Constraints**:
- Use Pydantic for configuration
- Support dev/prod environments
- Include API docs
- Handle exceptions globally

**Acceptance Criteria**:
- ✓ `uvicorn youtube_transcript.api.main:app` starts successfully
- ✓ `GET /health` returns `{"status": "ok"}`
- ✓ Swagger UI available at `/docs`
- ✓ ReDoc available at `/redoc`
- ✓ CORS configured correctly

**Verification**:
```bash
# Start server
uvicorn youtube_transcript.api.main:app --reload

# Test health endpoint
curl http://localhost:8000/health

# Test API docs
curl http://localhost:8000/docs
```

**Stop/Go Decision**: Proceed to Step 10

---

### Step 10: Implement Transcript API Endpoints

**Objective**: Create REST API endpoints for transcript fetching.

**Prerequisites**: Step 9 complete

**Test First**:
```
Test type: Integration
Test cases:
  ✓ Test POST /api/transcript with valid YouTube URL returns transcript
  ✓ Test POST /api/transcript with invalid URL returns 400
  ✓ Test POST /api/transcript with video without transcript returns 404
  ✓ Test POST /api/transcript with force_refresh query param
  ✓ Test that response includes metadata (video_id, language, created_at)
  ✓ Test that response is cached (second call faster)
Expected: Tests fail because endpoints don't exist
```

**Implementation**:
- Create request/response Pydantic models:
  - `TranscriptRequest`: `{ url: str, force_refresh?: bool }`
  - `TranscriptResponse`: `{ video_id: str, transcript: str, language: str, cached: bool, created_at: datetime }`
  - `ErrorResponse`: `{ error: str, detail: str }`
- Implement `POST /api/transcript` endpoint:
  - Validate URL
  - Extract video_id
  - Call TranscriptService
  - Return formatted response
- Add proper error handling (400, 404, 500)

**Scope**: POST endpoint for transcript fetching only

**Constraints**:
- Use FastAPI dependency injection
- Return proper HTTP status codes
- Include OpenAPI documentation
- Validate all inputs

**Acceptance Criteria**:
- ✓ Valid YouTube URL returns transcript
- ✓ Invalid URL returns 400 with error message
- ✓ Video without transcript returns 404
- ✓ Response includes all metadata
- ✓ Response format is consistent
- ✓ API docs show correct schemas

**Verification**:
```bash
# Run API tests
pytest tests/test_api/ -v

# Manual test
curl -X POST http://localhost:8000/api/transcript \
  -H "Content-Type: application/json" \
  -d '{"url": "https://youtu.be/dQw4w9WgXcQ"}'
```

**Stop/Go Decision**: Proceed to Step 11

---

## Phase 3: Web UI

---

### Step 11: Create HTML Templates with Jinja2

**Objective**: Design and implement HTML templates for the web interface.

**Prerequisites**: Step 10 complete

**Test First**:
```
Test type: Integration
Test cases:
  ✓ Test that home page renders without errors
  ✓ Test that form is present with correct input fields
  ✓ Test that error messages display correctly
  ✓ Test that transcript results display correctly
  ✓ Test that page is responsive (basic check)
Expected: Tests fail because templates don't exist
```

**Implementation**:
- Create `src/youtube_transcript/templates/` directory
- Create `base.html` with:
  - HTML5 structure
  - CSS (using Tailwind CDN or simple custom CSS)
  - HTMX CDN
  - Meta tags for responsiveness
- Create `index.html` with:
  - Form with URL input
  - "Fetch Transcript" button
  - Error message container
  - Transcript result container
  - Loading indicator
- Add minimal CSS for styling

**Scope**: Basic HTML templates, minimal styling

**Constraints**:
- Use Jinja2 templating
- Mobile-responsive design
- Include HTMX via CDN
- Keep CSS minimal (can enhance later)
- Accessible (semantic HTML, ARIA labels)

**Acceptance Criteria**:
- ✓ Templates render without errors
- ✓ Form has URL input and submit button
- ✓ Error/result containers exist
- ✓ Page loads successfully
- ✓ Basic styling applied

**Verification**:
```bash
# Run template tests
pytest tests/test_templates.py -v

# Manual test
curl http://localhost:8000/ | grep "Fetch Transcript"
```

**Stop/Go Decision**: Proceed to Step 12

---

### Step 12: Integrate HTMX for Dynamic Interactions

**Objective**: Add HTMX attributes to enable dynamic form submission without page reloads.

**Prerequisites**: Step 11 complete

**Test First**:
```
Test type: Integration (with web driver)
Test cases:
  ✓ Test that form submission doesn't reload page
  ✓ Test that loading indicator shows during fetch
  ✓ Test that transcript displays after successful fetch
  ✓ Test that error message displays on failure
  ✓ Test that form can be submitted multiple times
Expected: Tests fail because HTMX attributes not added
```

**Implementation**:
- Add HTMX attributes to form:
  - `hx-post="/api/transcript"`
  - `hx-target="#result"`
  - `hx-swap="innerHTML"`
  - `hx-indicator="#loading"`
- Create response templates:
  - `transcript_result.html` (partial for success)
  - `error_message.html` (partial for errors)
- Update API endpoint to return HTML for HTMX requests
- Add loading spinner

**Scope**: HTMX integration for form submission only

**Constraints**:
- Use HTMX, not JavaScript
- Progressive enhancement (works without HTMX)
- Return HTML for HTMX, JSON for API
- Show loading state
- Handle errors gracefully

**Acceptance Criteria**:
- ✓ Form submission is asynchronous
- ✓ Loading indicator shows during fetch
- ✓ Transcript displays without page reload
- ✓ Errors display without page reload
- ✓ Can submit multiple times
- ✓ Works with JavaScript disabled (graceful fallback)

**Verification**:
```bash
# Manual test in browser
# Open http://localhost:8000/
# Paste YouTube URL, click "Fetch Transcript"
# Verify: No page reload, loading shows, transcript appears
```

**Stop/Go Decision**: Proceed to Step 13

---

## Phase 4: CLI Tool

---

### Step 13: Implement CLI with Typer

**Objective**: Create command-line interface for transcript fetching.

**Prerequisites**: Step 8 complete (service layer)

**Test First**:
```
Test type: Integration
Test cases:
  ✓ Test that ytt command exists and shows help
  ✓ Test ytt <url> fetches and prints transcript
  ✓ Test ytt <url> --force-refresh bypasses cache
  ✓ Test ytt <url> --output saves to file
  ✓ Test ytt <url> with invalid URL shows error
  ✓ Test ytt <url> with unavailable transcript shows error
Expected: Tests fail because CLI doesn't exist
```

**Implementation**:
- Create `src/youtube_transcript/cli.py`
- Implement with Typer:
  - Main command: `ytt [URL]`
  - Options: `--force-refresh`, `--output FILE`, `--no-cache`
  - Output: print transcript to stdout
- Add `--version` option
- Add comprehensive help text
- Use Click's test runner for CLI testing

**Scope**: Basic CLI with core options

**Constraints**:
- Use Typer framework
- Share service layer with web API
- Clear error messages
- Support output to file
- Display progress indicators

**Acceptance Criteria**:
- ✓ `ytt --help` shows usage
- ✓ `ytt <url>` prints transcript
- ✓ `ytt <url> --output file.txt` saves to file
- ✓ `ytt <url> --force-refresh` bypasses cache
- ✓ Invalid URLs show helpful error
- ✓ Unavailable transcripts show clear message

**Verification**:
```bash
# Run CLI tests
pytest tests/test_cli.py -v

# Manual tests
ytt --help
ytt "https://youtu.be/dQw4w9WgXcQ"
ytt "https://youtu.be/dQw4w9WgXcQ" --output transcript.txt
```

**Stop/Go Decision**: Proceed to Step 14

---

## Phase 5: Polish and Deployment

---

### Step 14: Add Error Handling and Logging

**Objective**: Implement comprehensive error handling and structured logging.

**Prerequisites**: Step 13 complete

**Test First**:
```
Test type: Integration
Test cases:
  ✓ Test that all exceptions are caught and logged
  ✓ Test that user sees friendly error messages
  ✓ Test that sensitive data is not logged
  ✓ Test that logs are structured (JSON format)
  ✓ Test that log level can be configured
Expected: Tests fail because error handling not comprehensive
```

**Implementation**:
- Create `src/youtube_transcript/core/` directory
- Implement custom exception classes:
  - `YouTubeTranscriptError` (base)
  - `InvalidURLError`
  - `TranscriptUnavailableError`
  - `RateLimitError`
  - `CacheError`
  - `DatabaseError`
- Set up structured logging (structlog or python-json-logger)
- Create error handler middleware for FastAPI
- Add logging to all service methods
- Redact sensitive data (URLs can stay, but track errors)

**Scope**: Error handling and logging across all layers

**Constraints**:
- Never expose raw exceptions to users
- Log all errors with context
- Use structured logging (JSON)
- Support log level configuration
- Don't log sensitive data (though URLs are OK)

**Acceptance Criteria**:
- ✓ All exceptions are caught
- ✓ Users see friendly messages
- ✓ Logs are structured
- ✓ Log level configurable
- ✓ Errors are traceable

**Verification**:
```bash
# Test error logging
ytt "invalid-url" | grep "Error"

# Check logs
tail -f youtube-transcript.log | jq .
```

**Stop/Go Decision**: Proceed to Step 15

---

### Step 15: Add Docker Support

**Objective**: Containerize application for easy deployment.

**Prerequisites**: Step 14 complete

**Test First**:
```
Test type: Integration
Test cases:
  ✓ Test that Docker image builds successfully
  ✓ Test that container starts successfully
  ✓ Test that web service is accessible in container
  ✓ Test that CLI works in container
  ✓ Test that Redis connection works
  ✓ Test that database persists volumes
Expected: Tests fail because Docker files don't exist
```

**Implementation**:
- Create `Dockerfile`:
  - Multi-stage build (builder + runtime)
  - Install Python dependencies
  - Copy application code
  - Set ENTRYPOINT for web server
- Create `docker-compose.yml`:
  - Web service
  - Redis service
  - Database service (SQLite or PostgreSQL)
  - Volume mounts
  - Environment variables
- Create `.dockerignore`
- Add health checks

**Scope**: Docker containerization for development and production

**Constraints**:
- Use official Python base image
- Multi-stage build for smaller image
- Non-root user in container
- Health checks
- Volume mounts for data persistence

**Acceptance Criteria**:
- ✓ `docker build -t youtube-transcript .` succeeds
- ✓ `docker compose up` starts all services
- ✓ Web UI accessible at http://localhost:8000
- ✓ CLI works: `docker compose exec web ytt <url>`
- ✓ Redis connection works
- ✓ Database persists on restart

**Verification**:
```bash
# Build image
docker build -t youtube-transcript .

# Start services
docker compose up -d

# Test web UI
curl http://localhost:8000/health

# Test CLI
docker compose exec web ytt "https://youtu.be/dQw4w9WgXcQ"

# Check logs
docker compose logs web
```

**Stop/Go Decision**: Proceed to Step 16

---

### Step 16: Add Configuration Management

**Objective**: Implement flexible configuration system for multiple environments.

**Prerequisites**: Step 15 complete

**Test First**:
```
Test type: Unit
Test cases:
  ✓ Test that default configuration is valid
  ✓ Test that environment variables override defaults
  ✓ Test that .env file is loaded
  ✓ Test that configuration validates required fields
  ✓ Test that invalid configuration raises error
Expected: Tests fail because config system doesn't exist
```

**Implementation**:
- Create `src/youtube_transcript/config.py`
- Use Pydantic Settings:
  - Database URL
  - Redis URL
  - Cache TTL
  - Log level
  - API port
  - CORS origins
- Support environment variables
- Support `.env` file
- Validate configuration at startup
- Create example `.env.example`

**Scope**: Configuration for all environment variables

**Constraints**:
- Use Pydantic for validation
- Support multiple environments (dev, prod)
- Never commit secrets
- Provide sensible defaults
- Validate at startup

**Acceptance Criteria**:
- ✓ `.env.example` exists
- ✓ All environment variables documented
- ✓ Config validates on startup
- ✓ Defaults work for local dev
- ✓ Production config works with Docker

**Verification**:
```bash
# Test with defaults
python -c "from youtube_transcript.config import settings; print(settings)"

# Test with env vars
REDIS_URL=redis://localhost:6379/1 python -c "from youtube_transcript.config import settings; print(settings.redis_url)"
```

**Stop/Go Decision**: Proceed to Step 17

---

### Step 17: Write Documentation

**Objective**: Create comprehensive documentation for users and developers.

**Prerequisites**: Step 16 complete

**Test First**:
```
Test type: Manual
Test cases:
  ✓ README includes quick start guide
  ✓ README includes installation instructions
  ✓ README includes usage examples
  ✓ API docs are complete
  ✓ CLI docs are complete
  ✓ Development docs exist
Expected: Documentation doesn't exist or is incomplete
```

**Implementation**:
- Create comprehensive `README.md`:
  - Project overview
  - Quick start
  - Installation (pip, Docker)
  - Usage (Web UI, CLI, API)
  - Configuration
  - Development setup
  - Contributing
  - License
- Create `docs/` directory:
  - API.md (API endpoint documentation)
  - CLI.md (CLI usage)
  - ARCHITECTURE.md (system design)
  - DEPLOYMENT.md (deployment guide)
- Add inline code documentation
- Ensure OpenAPI docs are complete

**Scope**: User-facing and developer documentation

**Constraints**:
- Clear, concise language
- Include examples
- Keep README updated
- Document all configuration options
- Include troubleshooting section

**Acceptance Criteria**:
- ✓ README has all sections
- ✓ Installation works (step-by-step verified)
- ✓ Usage examples are accurate
- ✓ API docs match implementation
- ✓ CLI docs cover all options
- ✓ Deployment guide works

**Verification**:
```bash
# Follow README instructions
# Verify each step works as documented
```

**Stop/Go Decision**: Proceed to Step 18

---

### Step 18: Performance Testing and Optimization

**Objective**: Test and optimize performance to meet targets.

**Prerequisites**: Step 17 complete

**Test First**:
```
Test type: Performance
Test cases:
  ✓ Test cached response < 500ms (p95)
  ✓ Test uncached response < 10s (p95)
  ✓ Test URL parsing < 1ms
  ✓ Test cache hit rate > 80% (after 100 requests)
  ✓ Test concurrent requests (10 simultaneous)
Expected: Performance targets may not be met initially
```

**Implementation**:
- Create performance test suite:
  - Use `locust` or `pytest-benchmark`
  - Test cached/uncached responses
  - Test concurrent requests
  - Measure database query performance
- Profile code with `cProfile` or `py-spy`
- Optimize bottlenecks:
  - Add database indexes if needed
  - Optimize cache queries
  - Add connection pooling
- Set up performance monitoring

**Scope**: Performance testing and optimization

**Constraints**:
- Target: cached < 500ms, uncached < 10s
- Support 100+ concurrent requests
- Cache hit rate > 80%
- Don't optimize prematurely

**Acceptance Criteria**:
- ✓ Cached response p95 < 500ms
- ✓ Uncached response p95 < 10s
- ✓ Can handle 100 concurrent requests
- ✓ Cache hit rate > 80% for repeated requests
- ✓ No memory leaks

**Verification**:
```bash
# Run performance tests
pytest tests/test_performance.py -v

# Run load test
locust -f tests/locustfile.py --host=http://localhost:8000
```

**Stop/Go Decision**: Proceed to Step 19

---

### Step 19: Prepare for PyPI Release

**Objective**: Prepare CLI package for public PyPI release.

**Prerequisites**: Step 18 complete

**Test First**:
```
Test type: Manual
Test cases:
  ✓ Test that package builds successfully
  ✓ Test that package installs from local tarball
  ✓ Test that CLI command works after install
  ✓ Test that all dependencies are declared
  ✓ Test that package metadata is correct
Expected: Package not ready for PyPI
```

**Implementation**:
- Update `pyproject.toml`:
  - Add PyPI metadata
  - Set entry points for CLI
  - Declare all dependencies
  - Add classifiers
- Create `README.md` for PyPI page
- Create `MANIFEST.in` if needed
- Add version badge to README
- Test build: `python -m build`
- Test install: `pip install dist/youtube_transcript_tools-*.whl`
- Create TestPyPI account
- Publish to TestPyPI first
- Test install from TestPyPI
- Publish to PyPI

**Scope**: Package CLI for public PyPI distribution

**Constraints**:
- Follow PyPI best practices
- Use semantic versioning
- Include LICENSE file
- Include comprehensive README
- Test thoroughly before publishing

**Acceptance Criteria**:
- ✓ `pip install youtube-transcript-tools` works
- ✓ `ytt --help` works after install
- ✓ Package description is clear
- ✓ Version is correct
- ✓ Dependencies install correctly

**Verification**:
```bash
# Build package
python -m build

# Test local install
pip install dist/youtube_transcript_tools-*.whl
ytt --help

# Test PyPI (after publishing)
pip install youtube-transcript-tools
```

**Stop/Go Decision**: Proceed to Step 20

---

### Step 20: Final Testing and Release

**Objective**: Comprehensive end-to-end testing and production deployment.

**Prerequisites**: Step 19 complete

**Test First**:
```
Test type: End-to-End
Test cases:
  ✓ Test full user journey (Web UI)
  ✓ Test full user journey (CLI)
  ✓ Test full user journey (API)
  ✓ Test with various YouTube URL formats
  ✓ Test error scenarios
  ✓ Test deployment to production
Expected: Some edge cases may fail
```

**Implementation**:
- Create E2E test suite:
  - Web UI: Use Playwright or Selenium
  - CLI: Script tests
  - API: Integration tests
- Test with real YouTube videos:
  - Standard video
  - Short
  - Live stream
  - Video with manual captions
  - Video with auto captions
  - Video without captions
- Test error scenarios:
  - Invalid URL
  - Private video
  - Deleted video
  - Rate limiting
- Deploy to production:
  - Choose platform (Render, Railway, AWS, etc.)
  - Set up monitoring
  - Set up error tracking (Sentry)
  - Set up logging
- Smoke test in production

**Scope**: Final testing and production deployment

**Constraints**:
- Test all user-facing features
- Test common error scenarios
- Monitor production after deployment
- Have rollback plan ready
- Document deployment process

**Acceptance Criteria**:
- ✓ All E2E tests pass
- ✓ Web UI works in production
- ✓ CLI works (PyPI install)
- ✓ API works
- ✓ Monitoring is set up
- ✓ Error tracking is configured
- ✓ Documentation is updated

**Verification**:
```bash
# Run E2E tests
pytest tests/test_e2e/ -v

# Deploy to production
# (platform-specific commands)

# Smoke test
curl https://your-app.com/health
ytt "https://youtu.be/dQw4w9WgXcQ"
```

**Stop/Go Decision**: 🎉 **PROJECT COMPLETE**

---

## Summary

### Total Steps: 20

**Phases**:
- Phase 0: Project Setup and Infrastructure (Steps 1-4)
- Phase 1: Core Transcript Fetching (Steps 5-8)
- Phase 2: Web API (Steps 9-10)
- Phase 3: Web UI (Steps 11-12)
- Phase 4: CLI Tool (Steps 13)
- Phase 5: Polish and Deployment (Steps 14-20)

### Success Metrics

| Metric | Target | How to Measure |
|--------|--------|----------------|
| **Code Coverage** | > 80% | `pytest --cov` |
| **Cached Response** | p95 < 500ms | Performance tests |
| **Uncached Response** | p95 < 10s | Performance tests |
| **URL Parse Success** | > 99.5% | Test suite |
| **Cache Hit Rate** | > 80% | Monitoring |
| **All Tests Pass** | 100% | CI/CD |

### Risk Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **YouTube blocks scraping** | Medium | High | Multiple libraries, graceful degradation |
| **Redis unavailable** | Low | Medium | Graceful degradation, continue without cache |
| **Rate limiting** | High | Low | Exponential backoff, respect limits |
| **URL format changes** | Low | Medium | Flexible regex, community patterns |
| **Deployment issues** | Medium | Medium | Docker, comprehensive testing |

### Next Steps After Approval

1. Review this plan
2. Ask clarifying questions
3. Begin Step 1: Initialize Project Structure
4. Follow TDD discipline strictly
5. Update plan as needed based on discoveries

---

## Appendix: Test Data

### YouTube Videos for Testing

| Video ID | Type | Transcript Available | Purpose |
|----------|------|---------------------|---------|
| `dQw4w9WgXcQ` | Standard | Yes (manual) | Happy path testing |
| `j9rZxAF3C0I` | Short | Yes (auto) | Shorts URL format |
| `8hBmepWUJoc` | Live | Varies | Live stream testing |
| (private video) | Private | No | Error handling |
| (deleted video) | Deleted | No | Error handling |

### URL Formats to Test

All formats from the GitHub gist (100+ variations):
- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://www.youtube.com/shorts/VIDEO_ID`
- `https://www.youtube.com/live/VIDEO_ID`
- `https://www.youtube.com/embed/VIDEO_ID`
- Plus 95+ more variations

---

**End of Implementation Plan**

Ready to begin execution upon approval.
