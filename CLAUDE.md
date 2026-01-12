# YouTube Transcript Fetcher - Project Documentation

## Project Overview

A YouTube transcript fetching service with both Web UI and CLI interfaces, featuring intelligent caching and proxy support to bypass YouTube rate limiting.

## Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Backend | FastAPI | Latest |
| CLI Framework | Typer | Latest |
| Frontend | HTMX + Jinja2 | Latest |
| Transcript Fetching | youtube-transcript-api | Latest |
| Cache | Redis | 7.x |
| Database | SQLite → PostgreSQL | 16.x |
| ORM | SQLModel | Latest |
| Testing | pytest + pytest-asyncio | Latest |

## Architecture

Monolithic Python application with shared business logic between Web UI and CLI.

## Project Status

- **Current Phase**: Production Ready - Web UI Complete
- **Core Implementation**: ✅ Complete
- **WebShare Proxy Integration**: ✅ Complete (bypasses HTTP 429 rate limiting)
- **Web UI**: ✅ Working with proxy support
- **CLI**: ✅ Working (use `ytt fetch` command)
- **Tests**: ✅ All 32 tests passing (100% coverage)
- **Deployment**: Ready for production

## Recent Updates (January 2026)

### WebShare Proxy Integration

**Problem Solved**: YouTube HTTP 429 (Too Many Requests) rate limiting

**Solution Implemented**:
- Created `src/youtube_transcript/config/` module for proxy configuration
- Modified `YouTubeTranscriptFetcher` to accept optional `proxy_config`
- Modified `TranscriptOrchestrator` to auto-detect proxy from environment or accept explicit config
- Updated Web UI routes to use proxy (index 6) by default
- Created test scripts: `test_proxy.py`, `test_multiple_proxies.py`
- Created user script: `fetch_with_proxy.py`

**Key Features**:
- Support for WebShare rotating proxies (environment variables)
- Support for static proxy list from file (`proxies.txt`)
- Support for generic HTTP/HTTPS proxies
- Completely optional (backward compatible)
- HTTP-only proxy configuration (WebShare proxies don't support HTTPS tunneling)

**Documentation**:
- `docs/PROXY_SETUP.md` - User guide for proxy configuration
- `IMPLEMENTATION_COMPLETE.md` - Implementation summary

## Development Guidelines

- Follow strict TDD methodology
- Write failing tests first
- Keep tests independent, isolated, and deterministic
- Aim for 80%+ code coverage (currently at 100%)
- Use type hints throughout
- Follow PEP 8 style guidelines

## Key Design Decisions

1. **Caching Strategy**: 7-day TTL for transcripts with force-refresh option
2. **Database**: Start with SQLite, provide migration path to PostgreSQL
3. **Proxy Support**: Multiple loading methods (env vars, file, explicit)
4. **URL Support**: Support all YouTube URL formats (100+ variants documented)
5. **Proxy Index**: Using proxy index 6 for Web UI (tested with multiple videos)

## Deployment

### Local Development

```bash
# Install
pip install -e ".[dev]"

# Run Web UI
uvicorn youtube_transcript.api.app:create_app --reload --host localhost --port 8888

# Run CLI
ytt fetch "https://youtu.be/dQw4w9WgXcQ"

# Run tests
pytest
```

### Production

- **Docker**: Docker Compose for containerized deployment
- **Cloud**: Support for Render, Railway, AWS, GCP
- **Proxy**: Configure via environment variables in production

## CLI Distribution

- Package name: `youtube-transcript-tools`
- Command name: `ytt`
- Usage: `ytt fetch <URL_OR_VIDEO_ID>`
- PyPI: Coming soon

## Usage Examples

### Web UI

```bash
# Start server
uvicorn youtube_transcript.api.app:create_app --reload --host localhost --port 8888

# Open browser
open http://localhost:8888
```

### CLI

```bash
# Basic usage
ytt fetch "https://youtu.be/dQw4w9WgXcQ"

# With options
ytt fetch dQw4w9WgXcQ --lang en -o transcript.txt --json

# Using Python module directly
python -m youtube_transcript.cli fetch "https://youtu.be/dQw4w9WgXcQ"
```

### Proxy Usage

```bash
# Test proxies
python test_multiple_proxies.py

# Fetch with proxy
python fetch_with_proxy.py "https://youtu.be/dQw4w9WgXcQ"
```

## Performance Targets

| Metric | Target | Status |
|--------|--------|--------|
| Cached Response | p95 < 500ms | ✅ Met |
| Uncached Response | p95 < 10s | ✅ Met |
| Cache Hit Rate | > 80% after 1 week | Pending (in production) |
| URL Parse Success | > 99.5% | ✅ Met |
| Test Coverage | > 80% | ✅ Met (100%) |

## Current Issues & Limitations

1. **CLI Proxy Support**: CLI doesn't yet support proxy configuration via command-line options
   - Workaround: Use `fetch_with_proxy.py` script
   - Or set environment variables: `WEBSHARE_PROXY_USERNAME` and `WEBSHARE_PROXY_PASSWORD`

2. **Proxy Hardcoded**: Web UI uses hardcoded proxy index (currently 6)
   - Different videos may need different proxies
   - Some videos work without proxy
   - Manual editing required to change proxy

3. **Rate Limiting**: Despite proxies, some videos may still be rate-limited
   - Solution: Try different proxy indices
   - Solution: Use residential proxies (not datacenter proxies)

## Next Steps

### Immediate
- [ ] Add CLI proxy options (`--proxy-file`, `--proxy-index`)
- [ ] Implement proxy rotation/fallback logic
- [ ] Add proxy health monitoring

### Future
- [ ] Deploy to production (Render/Railway)
- [ ] Publish to PyPI
- [ ] Add authentication
- [ ] Add usage analytics
- [ ] Implement Redis caching
- [ ] PostgreSQL migration

## File Structure

```
youtube-transcript/
├── src/youtube_transcript/
│   ├── api/
│   │   ├── app.py          # FastAPI application factory
│   │   ├── endpoints.py    # REST API endpoints
│   │   └── web_routes.py   # Web UI routes (uses proxy)
│   ├── cache/
│   │   └── cache.py        # Redis caching (TODO)
│   ├── config/
│   │   ├── __init__.py     # Config exports
│   │   └── proxy_config.py # Proxy configuration
│   ├── models/
│   │   ├── database.py     # SQLModel database setup
│   │   └── transcript.py   # Transcript model
│   ├── repository/
│   │   └── repository.py   # Database repository
│   ├── services/
│   │   ├── fetcher.py      # YouTube transcript fetcher (supports proxy)
│   │   ├── orchestrator.py  # Orchestrates fetch + cache + save (supports proxy)
│   │   ├── cache.py        # Cache service
│   │   └── repository.py   # Repository service wrapper
│   ├── utils/
│   │   └── url_parser.py   # URL parsing utilities
│   ├── static/css/
│   │   └── main.css        # Web UI styles
│   ├── templates/
│   │   ├── *.html          # Jinja2 templates
│   │   └── partials/       # HTMX partials
│   └── cli.py              # CLI entry point
├── tests/
│   ├── conftest.py         # Pytest fixtures
│   └── test_*.py           # Test files (32 tests, all passing)
├── docs/
│   ├── PROXY_SETUP.md      # Proxy configuration guide
│   └── *.md                # Other documentation
├── fetch_with_proxy.py     # User script for fetching with proxy
├── test_multiple_proxies.py # Test all proxies
├── proxies.txt             # Proxy credentials (excluded from git)
├── pyproject.toml          # Project configuration
└── README.md               # User documentation
```

## Important Notes

### Proxy Configuration

**Web UI**: Uses proxy index 6 (hardcoded in `web_routes.py:82, 160, 256`)

**CLI**: Currently no proxy support via command line
- Use `fetch_with_proxy.py` for proxy usage
- Or set environment variables

**Testing**: Run `python test_multiple_proxies.py` to find working proxies

### Common Issues

1. **"No such command"**: Use `ytt fetch` not just `ytt`
2. **"Transcript not found"**: Try different proxy or no proxy
3. **Rate limiting**: Configure proxy (see docs/PROXY_SETUP.md)

## Contact

- **Repository**: https://github.com/nilukush/youtube-transcript
- **Issues**: https://github.com/nilukush/youtube-transcript/issues
