# Using WebShare Proxies

## Problem

YouTube returns HTTP 429 (Too Many Requests) when fetching transcripts due to rate limiting.

## Solution

Use WebShare residential proxies to bypass rate limiting.

## Quick Start

### 1. Get Your WebShare Proxies

You have a proxy list file with format:
```
IP:PORT:USERNAME:PASSWORD
```

Example:
```
198.23.239.134:6540:sqitehmd:kc8qw8dmu2m9
```

### 2. Test Your Proxies

```bash
python test_multiple_proxies.py
```

This will test all proxies and show which ones work.

### 3. Use Working Proxy in Code

```python
from youtube_transcript.models import get_session
from youtube_transcript.services import TranscriptOrchestrator
from youtube_transcript.config import setup_proxy_from_file

# Use proxy index 2 (the 3rd proxy) - this one works!
proxy_config = setup_proxy_from_file("proxies.txt", proxy_index=2)

# Initialize with proxy
session_gen = get_session()
session = next(session_gen)
orchestrator = TranscriptOrchestrator(
    session=session,
    proxy_config=proxy_config
)

# Fetch transcript
result = orchestrator.get_transcript('dQw4w9WgXcQ')
print(result.transcript)
```

### 4. CLI Usage

```python
from youtube_transcript.cli import app, fetch_transcript
from youtube_transcript.config import setup_proxy_from_file
import typer

# Override the fetcher with proxy
proxy_config = setup_proxy_from_file("proxies.txt", proxy_index=2)
from youtube_transcript.services import YouTubeTranscriptFetcher

# Create custom fetcher with proxy
fetcher = YouTubeTranscriptFetcher(proxy_config=proxy_config)

# Use in your CLI call
url = "https://youtu.be/dQw4w9WgXcQ"
result = fetcher.fetch_transcript('dQw4w9WgXcQ')
print(result.transcript)
```

## Important Notes

1. **Not All Proxies Work**: Some proxies may be blocked by YouTube
2. **Test First**: Always run `test_multiple_proxies.py` to find working proxies
3. **Use Proxy Index**: The working proxy index may change over time
4. **Free Tier**: Your 10 free proxies have limits

## Environment Variables (Optional)

If you have WebShare rotating proxy service (NOT static proxy list):

```bash
export WEBSHARE_PROXY_USERNAME="your_username"
export WEBSHARE_PROXY_PASSWORD="your_password"
```

Then the application will automatically use rotating proxies.

## Troubleshooting

### No Transcript Returned

- Try a different proxy index (0-9)
- Check if the video actually has transcripts
- Your proxy might be blocked - try another

### Proxy Connection Error

- Check your internet connection
- Verify the proxy credentials are correct
- Try a different proxy from your list

### All Proxies Blocked

- You may need to purchase residential proxies
- Static proxies get blocked quickly
- Rotating residential proxies work best

## Working Proxy

Based on testing, **proxy index 2** (`198.23.239.134:6540`) currently works.
