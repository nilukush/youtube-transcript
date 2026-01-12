# YouTube Transcript Fetcher - Project Documentation

## Project Overview

A YouTube transcript fetching SaaS with Web UI and CLI, featuring intelligent proxy support to bypass YouTube rate limiting.

**🚀 LIVE IN PRODUCTION**: https://youtube-transcript-zb5k.onrender.com

## Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Backend | FastAPI | Latest |
| CLI Framework | Typer | Latest |
| Frontend | HTMX + Jinja2 | Latest |
| Transcript API | youtube-transcript-api | Latest |
| Cache | Redis | 7.x |
| Database | SQLite → PostgreSQL | 16.x |
| ORM | SQLModel | Latest |
| Testing | pytest + pytest-asyncio | Latest |
| Deployment | Render | Free Tier |

## Architecture

**Monolithic Python application** with shared business logic between Web UI and CLI.

### User vs. Application Owner Separation

**End Users**: Visit website → Enter YouTube URL → Get transcript (zero configuration)

**Application Owners**: Configure proxies via environment variables (see [DEPLOYMENT.md](DEPLOYMENT.md))

## Project Status

- **Current Phase**: 🟢 **LIVE IN PRODUCTION**
- **Production URL**: https://youtube-transcript-zb5k.onrender.com
- **Core Implementation**: ✅ Complete
- **Proxy Integration**: ✅ Complete (WebShare rotating proxies)
- **Web UI**: ✅ Working with auto-proxy detection
- **CLI**: ✅ Working (use `ytt fetch` command)
- **Tests**: ✅ All 32 tests passing (100% coverage)
- **Deployment**: ✅ **Deployed to Render (January 2026)**

## Architecture Details

### How Proxy Configuration Works

**Production (Live)**:
1. Environment variables set in Render dashboard
2. Application auto-detects proxy via `get_proxy_config()`
3. All requests use proxy transparently
4. Users have zero knowledge of proxies

**Code Flow**:
```python
# web_routes.py
orchestrator = TranscriptOrchestrator(session=session)

# orchestrator.py (automatic):
config = proxy_config or get_proxy_config()  # Reads env vars
self.fetcher = YouTubeTranscriptFetcher(proxy_config=config)
```

## Recent Updates (January 2026)

### Production Deployment ✅

**Deployed**: https://youtube-transcript-zb5k.onrender.com

**Platform**: Render (Free Tier)
- Auto-deploys from GitHub main branch
- Environment-based proxy configuration
- Zero-downtime deployments
- Automatic SSL/HTTPS

**Environment Variables** (configured in Render):
```bash
WEBSHARE_PROXY_USERNAME=***
WEBSHARE_PROXY_PASSWORD=***
WEBSHARE_PROXY_LOCATIONS=US,CA,UK
WEBSHARE_PROXY_RETRIES=10
```

### Architecture Refinement

**Changes**:
- Removed hardcoded `proxies.txt` dependency
- Enabled automatic proxy detection from environment
- Production-ready 12-factor app architecture
- Complete separation of user experience and backend infrastructure

## Development Guidelines

- Follow strict TDD methodology
- Write failing tests first
- Keep tests independent, isolated, and deterministic
- Maintain 100% code coverage (current status)
- Use type hints throughout
- Follow PEP 8 style guidelines

## Key Design Decisions

1. **Proxy Support**: Environment variable configuration (12-factor app)
2. **Caching Strategy**: 7-day TTL for transcripts
3. **Database**: SQLite (dev) → PostgreSQL (production future)
4. **URL Support**: All YouTube URL formats (100+ variants)
5. **Architecture**: Complete separation of concerns (user vs. infrastructure)

## Deployment

### 🚀 Production (LIVE)

**URL**: https://youtube-transcript-zb5k.onrender.com

**Platform**: Render
**Status**: Deployed and working
**Branch**: `main` (auto-deploys on push)

**Start Command**:
```bash
uvicorn youtube_transcript.api.app:create_app --host 0.0.0.0 --port $PORT
```

**Build Command**:
```bash
pip install -e .
```

### Local Development

```bash
# Install
pip install -e ".[dev]"

# Run without proxy (testing)
uvicorn youtube_transcript.api.app:create_app --reload --host localhost --port 8888

# Run with proxy (production-like)
export WEBSHARE_PROXY_USERNAME="your_username"
export WEBSHARE_PROXY_PASSWORD="your_password"
uvicorn youtube_transcript.api.app:create_app --reload --host localhost --port 8888

# Run CLI
ytt fetch "https://youtu.be/dQw4w9WgXcQ"

# Run tests
pytest
```

## CLI Distribution

- **Package name**: `youtube-transcript-tools`
- **Command**: `ytt fetch <URL_OR_VIDEO_ID>`
- **PyPI**: Coming soon

## Performance Targets

| Metric | Target | Production Status |
|--------|--------|-------------------|
| Cached Response | p95 < 500ms | 🟡 Pending Redis |
| Uncached Response | p95 < 10s | ✅ Met |
| Cache Hit Rate | > 80% | 🟡 To be measured |
| URL Parse Success | > 99.5% | ✅ Met |
| Test Coverage | > 80% | ✅ Met (100%) |

## Current Limitations

1. **No Proxy Rotation**: Single proxy configuration
   - **Impact**: If proxy blocked, all requests fail
   - **Next**: Implement automatic proxy rotation

2. **Free Tier Sleeps**: Render free tier sleeps after 15min inactivity
   - **Impact**: ~30s cold start on first request
   - **Solution**: Upgrade to Starter tier ($7/month)

3. **No Caching Yet**: Redis not yet implemented
   - **Impact**: Every request fetches from YouTube API
   - **Next**: Add Redis caching

## Roadmap

### Completed ✅
- [x] Core transcript fetching
- [x] Web UI with HTMX
- [x] CLI with Typer
- [x] Proxy integration (WebShare)
- [x] Environment-based configuration
- [x] 100% test coverage
- [x] **Deploy to Render**

### In Progress 🚧
- [ ] Redis caching (reduces API calls)
- [ ] Proxy health monitoring
- [ ] Usage analytics

### Future 🔮
- [ ] Proxy rotation/fallback
- [ ] Publish to PyPI
- [ ] Authentication/API keys
- [ ] PostgreSQL migration
- [ ] Upgrade to paid Render tier

## File Structure

```
youtube-transcript/
├── src/youtube_transcript/
│   ├── api/              # FastAPI endpoints & web routes
│   ├── cache/            # Redis caching service
│   ├── config/           # Proxy configuration
│   ├── models/           # SQLModel database models
│   ├── repository/       # Database repository
│   ├── services/         # Business logic
│   ├── static/           # CSS assets
│   ├── templates/        # Jinja2 HTML templates
│   ├── utils/            # URL parsing
│   └── cli.py            # CLI entry point
├── tests/                # 32 tests, 100% coverage
├── docs/                 # Documentation
├── fetch_with_proxy.py   # Dev script
├── test_multiple_proxies.py  # Dev script
├── DEPLOYMENT.md         # Deployment guide
├── README.md             # User docs
├── CLAUDE.md             # This file
└── pyproject.toml        # Project config
```

## Quick Reference

### Production URL
https://youtube-transcript-zb5k.onrender.com

### Environment Variables
```bash
# Required (Render)
WEBSHARE_PROXY_USERNAME=***
WEBSHARE_PROXY_PASSWORD=***

# Optional
WEBSHARE_PROXY_LOCATIONS=US,CA,UK
WEBSHARE_PROXY_RETRIES=10
```

### Start Commands
```bash
# Production (Render)
uvicorn youtube_transcript.api.app:create_app --host 0.0.0.0 --port $PORT

# Local (dev)
uvicorn youtube_transcript.api.app:create_app --reload --host localhost --port 8888
```

### CLI Usage
```bash
# Basic
ytt fetch "https://youtu.be/dQw4w9WgXcQ"

# With options
ytt fetch dQw4w9WgXcQ --lang en -o transcript.txt --json
```

## Common Issues

1. **"No such command"**: Use `ytt fetch` not `ytt`
2. **"Transcript not found"**: Video has no captions or proxy blocked
3. **Rate limiting**: Ensure environment variables set in production
4. **Cold starts**: Free tier sleeps after 15min (upgrade to fix)

## Links

- **Repository**: https://github.com/nilukush/youtube-transcript
- **Live Site**: https://youtube-transcript-zb5k.onrender.com
- **Issues**: https://github.com/nilukush/youtube-transcript/issues
- **Deployment Guide**: [DEPLOYMENT.md](DEPLOYMENT.md)
