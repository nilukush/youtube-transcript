#!/usr/bin/env python3
"""Test all proxies to find a working one."""

from youtube_transcript.config import load_proxies_from_file, setup_proxy_from_file
from youtube_transcript.services import YouTubeTranscriptFetcher

proxy_file = "proxies.txt"
proxies = load_proxies_from_file(proxy_file)

print(f"Testing {len(proxies)} proxies...")
print("=" * 80)

video_id = 'dQw4w9WgXcQ'

for i, proxy in enumerate(proxies):
    print(f"\n[{i+1}/{len(proxies)}] Testing proxy: {proxy['ip']}:{proxy['port']}")

    config = setup_proxy_from_file(proxy_file, proxy_index=i)
    fetcher = YouTubeTranscriptFetcher(proxy_config=config)

    try:
        result = fetcher.fetch_transcript(video_id, languages=['en'])

        if result:
            print(f"  ✓✓✓ SUCCESS! ✓✓✓")
            print(f"  Video ID: {result.video_id}")
            print(f"  Language: {result.language}")
            print(f"  Type: {result.transcript_type}")
            print(f"  Duration: {result.duration}s")
            print(f"  Preview: {result.transcript[:100]}...")
            print(f"\n  ✓ Proxy #{i} works! Use this one.")
            break
        else:
            print(f"  ✗ No transcript returned")
    except Exception as e:
        print(f"  ✗ Error: {type(e).__name__}: {str(e)[:80]}")
else:
    print("\n✗ None of the proxies worked. This could mean:")
    print("  - All proxies are blocked by YouTube")
    print("  - The proxies don't support HTTPS tunneling")
    print("  - You need residential proxies (not datacenter proxies)")

print("\n" + "=" * 80)
