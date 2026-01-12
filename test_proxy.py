#!/usr/bin/env python3
"""Quick test script to verify WebShare proxy functionality."""

import sys
import os

# Test 1: Load proxies from file
print("=" * 80)
print("TEST 1: Loading Proxies from File")
print("=" * 80)

from youtube_transcript.config import load_proxies_from_file, setup_proxy_from_file

# Replace with your actual file path
proxy_file = "proxies.txt"  # Change this to your file path

if not os.path.exists(proxy_file):
    print(f"✗ ERROR: Proxy file not found: {proxy_file}")
    print(f"  Please create a file named 'proxies.txt' with one proxy per line:")
    print(f"  IP:PORT:USERNAME:PASSWORD")
    print(f"  Example: 142.111.48.253:7030:sqitehmd:kc8qw8dmu2m9")
    sys.exit(1)

proxies = load_proxies_from_file(proxy_file)
print(f"✓ Loaded {len(proxies)} proxies from {proxy_file}")
print(f"  First proxy: {proxies[0]['ip']}:{proxies[0]['port']}")

# Test 2: Setup proxy config
print("\n" + "=" * 80)
print("TEST 2: Setting up Proxy Configuration")
print("=" * 80)

config = setup_proxy_from_file(proxy_file, proxy_index=0)
if config:
    print(f"✓ Proxy configuration created successfully")
    print(f"  HTTP URL: {config.http_url}")
    print(f"  HTTPS URL: {config.https_url}")
else:
    print("✗ Failed to create proxy configuration")
    sys.exit(1)

# Test 3: Fetch transcript with proxy
print("\n" + "=" * 80)
print("TEST 3: Fetching YouTube Transcript with Proxy")
print("=" * 80)

from youtube_transcript.services import YouTubeTranscriptFetcher

fetcher = YouTubeTranscriptFetcher(proxy_config=config)

video_id = 'dQw4w9WgXcQ'
print(f"Fetching transcript for video: {video_id}")
print("This may take 10-30 seconds...")

try:
    result = fetcher.fetch_transcript(video_id, languages=['en'])

    if result:
        print("\n✓✓✓ SUCCESS! ✓✓✓")
        print(f"  Video ID: {result.video_id}")
        print(f"  Language: {result.language}")
        print(f"  Type: {result.transcript_type}")
        print(f"  Duration: {result.duration}s")
        print(f"  Transcript preview: {result.transcript[:150]}...")
        print("\n✓ Proxy is working! Your application can now fetch transcripts!")
    else:
        print("\n✗ Failed: No transcript returned")
        print("  This could mean:")
        print("  - The proxy doesn't work")
        print("  - The video has no transcript")
        print("  - YouTube is still blocking requests")
except Exception as e:
    print(f"\n✗ Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
