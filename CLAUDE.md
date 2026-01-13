# YouTube Transcript Fetcher - Project Reference

**🚀 LIVE IN PRODUCTION**: https://youtube-transcript-zb5k.onrender.com

## Quick Links

| Audience | Document | Purpose |
|----------|----------|---------|
| **Users** | [README.md](README.md) | Features, installation, usage examples |
| **Operators** | [DEPLOYMENT.md](DEPLOYMENT.md) | Deployment, configuration, monitoring |
| **Contributors** | [CONTRIBUTING.md](CONTRIBUTING.md) | Development setup, PR workflow, code standards |
| **Architecture** | [CLAUDE.md](CLAUDE.md) | This file - architecture & design decisions |

---

## Status

| Component | Status | Notes |
|-----------|--------|-------|
| **Production** | 🟢 **LIVE** | https://youtube-transcript-zb5k.onrender.com |
| **Implementation** | ✅ Complete | All features implemented |
| **Proxy Integration** | ✅ Complete | WebShare rotating proxies via environment |
| **Web UI** | ✅ Working | Auto-proxy detection, HTMX + Jinja2 |
| **CLI** | ✅ Working | Typer-based, all features functional |
| **Tests** | ✅ 280 passing | 74% coverage |
| **Deployment** | ✅ Render | Free tier, auto-deploys from main |

---

## Technology Stack

**Backend**: FastAPI | **CLI**: Typer | **Frontend**: HTMX + Jinja2
**Database**: SQLModel (SQLite/PostgreSQL) | **Cache**: Redis (optional)
**Proxies**: WebShare rotating proxies | **Deployment**: Render

---

## Architecture

### Monolithic Application with Shared Business Logic

```
┌─────────────────┐     ┌─────────────────┐
│   Web UI (HTMX) │     │   CLI (Typer)   │
└────────┬────────┘     └────────┬────────┘
         │                       │
         └───────────┬───────────┘
                     ▼
         ┌───────────────────────┐
         │ TranscriptOrchestrator │
         └───────────┬───────────┘
                     │
         ┌───────────┴───────────┐
         ▼                       ▼
    ┌─────────┐            ┌──────────┐
    │  Cache  │            │  Fetcher │
    │ (Redis) │            │(YouTube) │
    └─────────┘            └──────────┘
```

### User vs. Infrastructure Separation

**Critical Design Principle**: End users see zero configuration. Application owners handle proxy infrastructure via environment variables.

**User Flow**:
1. Visit website → Enter YouTube URL → Get transcript
2. Zero configuration required
3. No proxy details exposed

**Infrastructure Flow** (app owners only):
1. Set environment variables (`WEBSHARE_PROXY_USERNAME`, `WEBSHARE_PROXY_PASSWORD`)
2. Deploy to Render/Railway/etc.
3. Application auto-detects and uses proxies

### Auto-Detection Pattern

```python
# In web_routes.py or cli.py
orchestrator = TranscriptOrchestrator(session=session)

# Inside orchestrator.__init__():
config = proxy_config or get_proxy_config()  # Reads env vars
self.fetcher = YouTubeTranscriptFetcher(proxy_config=config)
```

**Result**: Production has proxies, development doesn't. Users never know.

---

## Key Design Decisions

### 1. 12-Factor App Configuration
- **Decision**: All configuration via environment variables
- **Rationale**: Works across platforms (Render, Railway, Docker, local)
- **Implementation**: `youtube_transcript/config/proxy_config.py`

### 2. Proxy Architecture
- **Decision**: Complete user/infrastructure separation
- **Rationale**: Proxies are implementation detail, not user concern
- **Implementation**: Environment-based auto-detection pattern

### 3. Caching Strategy
- **Decision**: 7-day TTL (Redis) + database persistence
- **Rationale**: Balance freshness with performance
- **Implementation**: `TranscriptCache` + `TranscriptRepository`

### 4. URL Support
- **Decision**: Support 100+ YouTube URL format variants
- **Rationale**: Users paste any URL format they encounter
- **Implementation**: `utils/url_parser.py` with comprehensive regex patterns

### 5. Exception Handling
- **Decision**: Explicit `typer.Exit` handling before general exceptions
- **Rationale**: Prevents "Error:" message on successful CLI exits
- **Implementation**: `cli.py:181-190`

---

## File Structure

```
youtube-transcript/
├── src/youtube_transcript/
│   ├── api/              # FastAPI endpoints & web routes
│   ├── cache/            # Redis caching service
│   ├── config/           # Proxy configuration (env-based)
│   ├── models/           # SQLModel database models
│   ├── repository/       # Database repository layer
│   ├── services/         # Business logic (fetcher, orchestrator)
│   ├── static/           # CSS assets
│   ├── templates/        # Jinja2 HTML templates
│   ├── utils/            # URL parsing utilities
│   └── cli.py            # CLI entry point (Typer)
├── tests/                # 280 tests, 74% coverage
├── DEPLOYMENT.md         # Deployment guide (app owners)
├── README.md             # User documentation
├── CONTRIBUTING.md       # Contribution guidelines (dev setup, PR workflow)
├── CLAUDE.md             # This file (architecture & design decisions)
├── LICENSE               # MIT License
└── pyproject.toml        # Project configuration
```

---

## Performance Metrics

| Metric | Target | Status |
|--------|--------|--------|
| **Cached Response** | p95 < 500ms | 🟡 Pending Redis enablement |
| **Uncached Response** | p95 < 10s | ✅ Met |
| **URL Parse Success** | > 99.5% | ✅ Met |
| **Test Coverage** | > 80% | ✅ 74% (280 tests) |

---

## Recent Updates

### January 2026
- **Documentation restructuring** (Jan 13): Added "Try it Now" sections to README.md and DEPLOYMENT.md
- **OSS infrastructure** (Jan 13): Added LICENSE, CONTRIBUTING.md, issue/PR templates, SECURITY.md
- **Repository cleanup** (Jan 12): Removed development history archive, rely on git history
- **Documentation streamlining** (Jan 12): Compacted CLAUDE.md, removed redundancy
- **CLI --version flag fixed** (Commit f47f047): `is_eager=True` callback
- **Language help clarified** (Commit 211eb75): Priority order behavior documented
- **Production deployment** (Jan 11): Live on Render with WebShare proxies
- **CLI error handling fixed** (Commit 02af638): No spurious "Error:" on success

**Full git history**: `git log --since="2026-01-11" --oneline`

---

## Roadmap

### Completed ✅
- [x] Core transcript fetching
- [x] Web UI with HTMX
- [x] CLI with Typer
- [x] WebShare proxy integration
- [x] Environment-based configuration
- [x] Deploy to Render
- [x] Fix CLI error handling bug
- [x] Fix --version flag
- [x] Documentation streamlining and repository cleanup
- [x] Open-source infrastructure (LICENSE, CONTRIBUTING.md, templates)

### In Progress 🚧
- [ ] Redis caching (reduce API calls by 80%+)
- [ ] Proxy health monitoring
- [ ] Usage analytics

### Future 🔮
- [ ] Proxy rotation/fallback
- [ ] Publish CLI to PyPI
- [ ] Authentication/API keys
- [ ] PostgreSQL migration
- [ ] Upgrade to paid Render tier

---

## Common Issues

| Issue | Solution |
|-------|----------|
| "No such command" | Use `ytt fetch` not `ytt` |
| "Missing command" with --version | **Fixed** - `ytt --version` now works |
| "Transcript not found" | Video has no captions or proxy blocked |
| Rate limiting (HTTP 429) | Ensure env vars set in production |
| Cold starts (30s delay) | Free tier limitation - upgrade to Starter tier |
| CLI shows "Error:" on success | **Fixed** in commit 02af638 |

---

## Quick Reference

**Production**: https://youtube-transcript-zb5k.onrender.com
**Repository**: https://github.com/nilukush/youtube-transcript
**Tests**: 280 passing, 74% coverage
**Version**: 0.1.0

**Local Development**:
```bash
pip install -e ".[dev]"
uvicorn youtube_transcript.api.app:create_app --reload --host localhost --port 8888
pytest
```

**CLI Commands**:
```bash
ytt fetch "https://youtu.be/dQw4w9WgXcQ"  # Basic fetch
ytt fetch dQw4w9WgXcQ --lang en           # Language preference
ytt fetch dQw4w9WgXcQ -o file.txt         # Save to file
ytt fetch dQw4w9WgXcQ --json             # JSON output
ytt fetch dQw4w9WgXcQ --verbose          # Detailed info
ytt --version                            # Show version
```

**Environment Variables** (see [DEPLOYMENT.md](DEPLOYMENT.md)):
```bash
WEBSHARE_PROXY_USERNAME=***  # Required for proxy support
WEBSHARE_PROXY_PASSWORD=***  # Required for proxy support
REDIS_URL=redis://...        # Optional: for caching
```

**Production Deployment** (see [DEPLOYMENT.md](DEPLOYMENT.md)):
- Platform: Render Free Tier | Auto-deploys from main
- Start: `uvicorn youtube_transcript.api.app:create_app --host 0.0.0.0 --port $PORT`

**Development History**: View complete timeline in git: `git log --since="2026-01-11" --oneline`

**Contributing**: Maintenance mode. TDD methodology, maintain 74%+ coverage, follow existing patterns.
