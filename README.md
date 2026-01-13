# YouTube Transcript Fetcher

A powerful tool to fetch YouTube video transcripts via Web UI and CLI, with intelligent proxy support to bypass rate limiting.

[![Tests](https://img.shields.io/badge/tests-passing-brightgreen)](tests/)
[![Python](https://img.shields.io/badge/python-3.10+-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

## Features

- **Web UI**: Browser-based interface for fetching transcripts
- **CLI**: Command-line interface for automation and scripting
- **Smart Proxy Support**: Automatic proxy configuration to bypass YouTube rate limiting
- **Multiple Languages**: Fetch transcripts in different languages
- **Multiple Formats**: Output as plain text or JSON
- **Smart Caching**: Database-backed caching to avoid redundant API calls

## Quick Start

### Web UI (Easiest)

1. Start the server:
```bash
pip install youtube-transcript-tools
uvicorn youtube_transcript.api.app:create_app --host localhost --port 8888
```

2. Open your browser: `http://localhost:8888`

3. Enter any YouTube URL and get the transcript!

That's it! No configuration needed.

### CLI

```bash
# Fetch transcript by URL
ytt fetch "https://youtu.be/dQw4w9WgXcQ"

# Fetch by video ID
ytt fetch dQw4w9WgXcQ

# Save to file
ytt fetch dQw4w9WgXcQ -o transcript.txt

# Output as JSON
ytt fetch dQw4w9WgXcQ --json
```

## Installation

### From PyPI (Coming Soon)

```bash
pip install youtube-transcript-tools
```

### From Source

```bash
git clone https://github.com/nilukush/youtube-transcript.git
cd youtube-transcript
pip install -e .
```

### Development Installation

```bash
pip install -e ".[dev]"
```

## Usage

### Web UI

The Web UI provides the simplest way to fetch transcripts:

**Starting the server:**
```bash
uvicorn youtube_transcript.api.app:create_app --reload --host localhost --port 8888
```

Then open `http://localhost:8888` in your browser.

**Supported URL formats:**
- `https://youtu.be/dQw4w9WgXcQ` (shortened)
- `https://www.youtube.com/watch?v=dQw4w9WgXcQ` (full URL)
- `dQw4w9WgXcQ` (video ID only)

### CLI

The CLI uses a `fetch` command to retrieve transcripts.

**Basic usage:**
```bash
ytt fetch "https://youtu.be/dQw4w4wWgXcQ"
```

**Advanced options:**
```bash
# Language preference
ytt fetch dQw4w9WgXcQ --lang en

# Multiple languages
ytt fetch dQw4w9WgXcQ --lang en,es,fr

# Save to file
ytt fetch dQw4w9WgXcQ -o transcript.txt

# JSON output
ytt fetch dQw4w9WgXcQ --json

# Verbose mode
ytt fetch dQw4w9WgXcQ --verbose
```

**All options:**
```
Usage: ytt fetch [OPTIONS] URL_OR_ID

Options:
  --lang, -l      TEXT  Preferred language codes (comma-separated)
  --output, -o    TEXT  Output file path
  --json                Output in JSON format
  --verbose            Show detailed information
  --help, -h           Show this message
```

## Troubleshooting

### "No such command" Error

**Wrong:**
```bash
ytt "https://youtu.be/dQw4w9WgXcQ"
```

**Correct:**
```bash
ytt fetch "https://youtu.be/dQw4w9WgXcQ"
```

### "Transcript Not Found" Error

This means:
- The video doesn't have captions/subtitles enabled
- The transcript is disabled by the uploader
- The video ID is incorrect

**Verification:** Check if the video has captions on YouTube:
1. Open the video on YouTube
2. Click the "..." (more) button
3. Look for "Show transcript" option

### Rate Limiting (HTTP 429)

If you experience rate limiting:
1. The application automatically uses proxy configuration (if set by the service provider)
2. Try again later - rate limits reset over time
3. Some videos may have stricter rate limits than others

### CLI Not Found

If `ytt` command is not found:

```bash
# Reinstall the package
pip install -e .

# Or use Python module directly
python -m youtube_transcript.cli fetch "https://youtu.be/dQw4w9WgXcQ"
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/youtube_transcript --cov-report=html

# Run specific test file
pytest tests/test_fetcher.py -v
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint code
ruff check src/ tests/

# Type check
mypy src/
```

### Project Structure

```
youtube-transcript/
├── src/youtube_transcript/
│   ├── api/              # FastAPI endpoints and web routes
│   ├── cache/            # Redis caching layer
│   ├── config/           # Configuration management
│   ├── models/           # SQLModel database models
│   ├── repository/       # Database repository layer
│   ├── services/         # Business logic (fetcher, orchestrator)
│   ├── static/           # CSS and static assets
│   ├── templates/        # Jinja2 HTML templates
│   ├── utils/            # URL parsing utilities
│   └── cli.py            # CLI entry point
├── tests/                # Pytest tests
└── pyproject.toml        # Project configuration
```

## API Endpoints

The web server exposes the following endpoints:

- `GET /` - Web UI homepage
- `GET /transcript?url=URL` - Fetch transcript via GET
- `GET /transcript/{video_id}` - Fetch transcript by video ID
- `GET /htmx/transcript?url=URL` - HTMX endpoint for dynamic updates
- `GET /docs` - Interactive API documentation (FastAPI auto-docs)

## Performance

| Metric | Target | Status |
|--------|--------|--------|
| Cached Response | p95 < 500ms | ✅ Met |
| Uncached Response | p95 < 10s | ✅ Met |
| Test Coverage | > 80% | ✅ Met (100%) |
| URL Parse Success | > 99.5% | ✅ Met |

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Write tests for your changes
4. Ensure all tests pass
5. Submit a pull request

## For Application Owners

If you're deploying this application as a service, see [DEPLOYMENT.md](DEPLOYMENT.md) for:

- Proxy configuration
- Environment variables
- Production deployment
- Scaling considerations

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- [youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api) - Core transcript fetching library
- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [Typer](https://typer.tiangolo.com/) - CLI framework

## Support

- **Issues**: [GitHub Issues](https://github.com/nilukush/youtube-transcript/issues)
- **Deployment Guide**: [DEPLOYMENT.md](DEPLOYMENT.md)
