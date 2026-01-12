# YouTube Transcript Fetcher - Project Documentation

## Project Overview

A YouTube transcript fetching service with both Web UI and CLI interfaces, featuring intelligent caching to minimize redundant API calls.

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

## Development Guidelines

- Follow strict TDD methodology
- Write failing tests first
- Keep tests independent, isolated, and deterministic
- Aim for 80%+ code coverage
- Use type hints throughout
- Follow PEP 8 style guidelines

## Project Status

- **Current Phase**: Planning
- **Analysis**: Complete (see `docs/ANALYSIS.md`)
- **Implementation**: Pending

## Key Design Decisions

1. **Caching Strategy**: 7-day TTL for transcripts with force-refresh option
2. **Database**: Start with SQLite, provide migration path to PostgreSQL
3. **Authentication**: Optional, support both anonymous and authenticated users
4. **URL Support**: Support all YouTube URL formats (100+ variants documented)

## Deployment

- **Local**: Docker Compose for development
- **Cloud**: Support multiple platforms (Render, Railway, AWS, GCP)

## CLI Distribution

- Public PyPI package
- Command name: `ytt`

## Performance Targets

| Metric | Target |
|--------|--------|
| Cached Response | p95 < 500ms |
| Uncached Response | p95 < 10s |
| Cache Hit Rate | > 80% after 1 week |
| URL Parse Success | > 99.5% |
