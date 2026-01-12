# YouTube Transcript Fetcher

A powerful tool to fetch YouTube video transcripts via Web UI and CLI, with support for proxy configuration to bypass rate limiting.

[![Tests](https://img.shields.io/badge/tests-passing-brightgreen)](tests/)
[![Python](https://img.shields.io/badge/python-3.10+-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

## Features

- **Web UI**: Browser-based interface for fetching transcripts
- **CLI**: Command-line interface for automation and scripting
- **Proxy Support**: Built-in WebShare proxy integration to bypass YouTube rate limiting
- **Multiple Languages**: Fetch transcripts in different languages
- **Multiple Formats**: Output as plain text or JSON
- **Smart Caching**: Database-backed caching to avoid redundant API calls

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

Start the web server:

```bash
# Make sure the package is installed
pip install -e .

# Start the server
uvicorn youtube_transcript.api.app:create_app --reload --host localhost --port 8888
```

Then open your browser to: `http://localhost:8888`

#### Using the Web UI

1. Enter a YouTube URL in the form
2. Click "Fetch Transcript"
3. View or download the transcript

**Example URLs:**
- `https://youtu.be/dQw4w9WgXcQ`
- `https://www.youtube.com/watch?v=dQw4w9WgXcQ`
- `dQw4w9WgXcQ` (video ID only)

### CLI

The CLI uses a `fetch` command to retrieve transcripts.

#### Basic Usage

```bash
# Fetch transcript by URL
ytt fetch "https://youtu.be/dQw4w9WgXcQ"

# Fetch by video ID
ytt fetch dQw4w9WgXcQ
```

#### Advanced Options

```bash
# Specify language preference
ytt fetch dQw4w9WgXcQ --lang en

# Multiple languages (comma-separated)
ytt fetch dQw4w9WgXcQ --lang en,es,fr

# Save to file
ytt fetch dQw4w9WgXcQ -o transcript.txt

# Output as JSON
ytt fetch dQw4w9WgXcQ --json

# Verbose output
ytt fetch dQw4w9WgXcQ --verbose
```

#### All Options

```
Usage: ytt fetch [OPTIONS] URL_OR_ID

Fetch a transcript from a YouTube video.

╭─ Options ──────────────────────────────────────────────────────────────╮
│ --lang          -l      TEXT  Preferred language codes (comma-separated)│
│ --output        -o      TEXT  Output file path                         │
│ --json                       Output in JSON format                     │
│ --verbose                    Show detailed information                  │
│ --help          -h            Show this message and exit               │
╰────────────────────────────────────────────────────────────────────────╯
╭─ Arguments ────────────────────────────────────────────────────────────╮
│ URL_OR_ID      YouTube video URL or video ID                           │
╰────────────────────────────────────────────────────────────────────────╯
```

## Proxy Configuration

YouTube rate limits can prevent fetching transcripts. This tool includes built-in proxy support using WebShare proxies.

### Quick Setup

1. Create a `proxies.txt` file in your project root:

```
IP:PORT:USERNAME:PASSWORD
```

Example:
```
198.23.239.134:6540:your_username:your_password
```

2. **For Web UI**: The proxy is automatically configured. Edit `src/youtube_transcript/api/web_routes.py` to change the proxy index.

3. **For CLI**: Use the Python script directly:

```bash
python fetch_with_proxy.py "https://youtu.be/dQw4w9WgXcQ"
```

### Testing Proxies

Test all proxies to find working ones:

```bash
python test_multiple_proxies.py
```

### Environment Variables (Optional)

Set proxy via environment variables:

```bash
export WEBSHARE_PROXY_USERNAME="your_username"
export WEBSHARE_PROXY_PASSWORD="your_password"
```

### Documentation

See [docs/PROXY_SETUP.md](docs/PROXY_SETUP.md) for detailed proxy configuration guide.

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
│   ├── config/           # Proxy configuration
│   ├── models/           # SQLModel database models
│   ├── repository/       # Database repository layer
│   ├── services/         # Business logic (fetcher, orchestrator)
│   ├── static/           # CSS and static assets
│   ├── templates/        # Jinja2 HTML templates
│   ├── utils/            # URL parsing utilities
│   └── cli.py            # CLI entry point
├── tests/                # Pytest tests
├── docs/                 # Documentation
└── pyproject.toml        # Project configuration
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
- The video doesn't have captions/subtitles
- The transcript is disabled by the uploader
- The video ID is incorrect
- Your proxy is blocked (try a different proxy or no proxy)

### Rate Limiting (HTTP 429)

If you see rate limiting errors:
1. Configure a proxy (see Proxy Configuration above)
2. Try a different proxy from your list
3. Some videos may work without proxy

### CLI Not Found

If `ytt` command is not found:

```bash
# Reinstall the package
pip install -e .

# Or use Python module directly
python -m youtube_transcript.cli fetch "https://youtu.be/dQw4w9WgXcQ"
```

## API Endpoints

The web server exposes the following endpoints:

- `GET /` - Web UI homepage
- `GET /transcript?url=URL` - Fetch transcript via GET
- `GET /transcript/{video_id}` - Fetch transcript by video ID
- `GET /htmx/transcript?url=URL` - HTMX endpoint for dynamic updates
- `GET /docs` - API documentation (FastAPI auto-docs)

## Performance Targets

| Metric | Target | Current |
|--------|--------|---------|
| Cached Response | p95 < 500ms | ✓ Met |
| Uncached Response | p95 < 10s | ✓ Met |
| Test Coverage | > 80% | ✓ Met (100%) |
| URL Parse Success | > 99.5% | ✓ Met |

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Write tests for your changes
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- [youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api) - Core transcript fetching library
- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [Typer](https://typer.tiangolo.com/) - CLI framework
- [WebShare.io](https://www.webshare.io/) - Proxy service

## Support

- **Issues**: [GitHub Issues](https://github.com/nilukush/youtube-transcript/issues)
- **Documentation**: [docs/](docs/)
- **WebShare Proxy Guide**: [docs/PROXY_SETUP.md](docs/PROXY_SETUP.md)
