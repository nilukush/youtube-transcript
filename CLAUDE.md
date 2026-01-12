# YouTube Transcript Fetcher - Project Documentation

**🚀 LIVE IN PRODUCTION**: https://youtube-transcript-zb5k.onrender.com

## Project Overview

YouTube transcript fetching SaaS with Web UI and CLI. Intelligent proxy support bypasses YouTube rate limiting. Users get transcripts with zero configuration. Application owners configure proxies via environment variables.

**Technology Stack**: FastAPI | Typer CLI | HTMX + Jinja2 | SQLModel | Redis | WebShare Proxies | Render Deployment

## Status

| Component | Status | Notes |
|-----------|--------|-------|
| **Production** | 🟢 **LIVE** | https://youtube-transcript-zb5k.onrender.com |
| **Core Implementation** | ✅ Complete | All features working |
| **Proxy Integration** | ✅ Complete | WebShare rotating proxies |
| **Web UI** | ✅ Working | Auto-proxy detection |
| **CLI** | ✅ Working | Clean output (bug fixed) |
| **Tests** | ✅ 286 passing | 74% coverage |
| **Deployment** | ✅ Render | Auto-deploys from main |

## Architecture

**Monolithic Python application** with shared business logic between Web UI and CLI.

### User vs. Infrastructure Separation

- **End Users**: Visit website → Enter YouTube URL → Get transcript (zero config)
- **Application Owners**: Configure proxies via environment variables (see [DEPLOYMENT.md](DEPLOYMENT.md))

### Proxy Auto-Detection Flow

```python
# web_routes.py / cli.py
orchestrator = TranscriptOrchestrator(session=session)

# orchestrator.py (automatic):
config = proxy_config or get_proxy_config()  # Reads env vars
self.fetcher = YouTubeTranscriptFetcher(proxy_config=config)
```

**Result**: Production has proxies, development doesn't. Users never know.

## Production Deployment

**Platform**: Render Free Tier | **Branch**: main (auto-deploys on push)

**Environment Variables** (set in Render dashboard):
```bash
WEBSHARE_PROXY_USERNAME=***
WEBSHARE_PROXY_PASSWORD=***
WEBSHARE_PROXY_LOCATIONS=US,CA,UK
WEBSHARE_PROXY_RETRIES=10
```

**Start Command**: `uvicorn youtube_transcript.api.app:create_app --host 0.0.0.0 --port $PORT`

**Limitations**:
- Free tier sleeps after 15min inactivity (~30s cold starts)
- Upgrade to Starter ($7/mo) to eliminate cold starts

## Recent Updates (January 2026)

### ✅ Production Deployment
- Deployed to Render: https://youtube-transcript-zb5k.onrender.com
- Environment-based proxy configuration (12-factor app)
- Removed hardcoded `proxies.txt` dependency
- Complete user/infrastructure separation

### ✅ CLI Bug Fix (Commit 02af638)
**Issue**: Spurious "Error:" message appeared after successful transcript fetches.

**Root Cause**: `typer.Exit(code=0)` was caught by general `except Exception as e:` handler because `typer.Exit` inherits from `Exception`.

**Fix**:
```python
# Before (Lines 179-187)
raise typer.Exit(code=0)
except Exception as e:
    console.print(f"[red]Error:[/red] {str(e)}")

# After (Lines 179-190)
return  # Changed from raise Exit
except typer.Exit:
    raise  # Re-raise Exit exceptions first
except Exception as e:
    console.print(f"[red]Error:[/red] {str(e)}")
```

**Impact**: CLI now shows clean output on success. Error handling preserved for actual failures.

## Local Development

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
ytt fetch dQw4w9WgXcQ --lang en -o transcript.txt --json

# Run tests
pytest
```

## CLI Distribution

- **Package**: `youtube-transcript-tools` (PyPI coming soon)
- **Command**: `ytt fetch <URL_OR_VIDEO_ID>`
- **Exit Codes**: 0 = success, 1 = error
- **Output**: Plain text (default) or JSON (`--json`)

## Performance Metrics

| Metric | Target | Status |
|--------|--------|--------|
| Cached Response | p95 < 500ms | 🟡 Pending Redis |
| Uncached Response | p95 < 10s | ✅ Met |
| URL Parse Success | > 99.5% | ✅ Met |
| Test Coverage | > 80% | ✅ 74% (286 tests) |

## Roadmap

### Completed ✅
- [x] Core transcript fetching
- [x] Web UI with HTMX
- [x] CLI with Typer
- [x] WebShare proxy integration
- [x] Environment-based configuration
- [x] Deploy to Render
- [x] **Fix CLI error handling bug**

### In Progress 🚧
- [ ] Redis caching (reduce API calls by 80%+)
- [ ] Proxy health monitoring
- [ ] Usage analytics

### Future 🔮
- [ ] Proxy rotation/fallback
- [ ] Publish to PyPI
- [ ] Authentication/API keys
- [ ] PostgreSQL migration
- [ ] Upgrade to paid Render tier

## Common Issues

| Issue | Solution |
|-------|----------|
| "No such command" | Use `ytt fetch` not `ytt` |
| "Transcript not found" | Video has no captions or proxy blocked |
| Rate limiting (HTTP 429) | Ensure env vars set in production |
| Cold starts (30s delay) | Free tier sleeps - upgrade to Starter tier |
| CLI shows "Error:" on success | **Fixed** in commit 02af638 |

## File Structure

```
youtube-transcript/
├── src/youtube_transcript/
│   ├── api/              # FastAPI endpoints & web routes
│   ├── cache/            # Redis caching service
│   ├── config/           # Proxy configuration (env-based)
│   ├── models/           # SQLModel database models
│   ├── repository/       # Database repository layer
│   ├── services/         # Business logic (fetcher, orchestrator, cache)
│   ├── static/           # CSS assets
│   ├── templates/        # Jinja2 HTML templates
│   ├── utils/            # URL parsing utilities
│   └── cli.py            # CLI entry point (Typer)
├── tests/                # 286 tests, 74% coverage
├── DEPLOYMENT.md         # Deployment guide (app owners)
├── README.md             # User documentation
├── CLAUDE.md             # This file
└── pyproject.toml        # Project configuration
```

## Quick Reference

**Production**: https://youtube-transcript-zb5k.onrender.com
**Repository**: https://github.com/nilukush/youtube-transcript
**Deployment Guide**: [DEPLOYMENT.md](DEPLOYMENT.md)

**Environment Variables**:
```bash
WEBSHARE_PROXY_USERNAME=***  # Required for proxy support
WEBSHARE_PROXY_PASSWORD=***  # Required for proxy support
WEBSHARE_PROXY_LOCATIONS=US,CA,UK  # Optional: preferred countries
WEBSHARE_PROXY_RETRIES=10  # Optional: retry count
```

**CLI Commands**:
```bash
ytt fetch "https://youtu.be/dQw4w9WgXcQ"  # Basic fetch
ytt fetch dQw4w9WgXcQ --lang en  # Language preference
ytt fetch dQw4w9WgXcQ -o file.txt  # Save to file
ytt fetch dQw4w9WgXcQ --json  # JSON output
ytt fetch dQw4w9WgXcQ --verbose  # Detailed info
```

## Key Design Decisions

1. **12-Factor App**: Configuration via environment variables only
2. **Proxy Architecture**: Complete separation - users never see proxy details
3. **Caching Strategy**: 7-day TTL (Redis) + database persistence
4. **Database**: SQLite (dev) → PostgreSQL (production future)
5. **URL Support**: 100+ YouTube URL format variants
6. **Exception Handling**: Explicit `typer.Exit` handling before general exceptions
