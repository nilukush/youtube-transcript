#!/usr/bin/env python3
"""
Simple script to fetch YouTube transcript with proxy.

Usage:
    python fetch_with_proxy.py "https://youtu.be/VIDEO_ID"
"""

import sys
from youtube_transcript.models import get_session, init_db
from youtube_transcript.services import TranscriptOrchestrator
from youtube_transcript.config import setup_proxy_from_file
from youtube_transcript.utils.url_parser import extract_video_id

def main():
    if len(sys.argv) < 2:
        print("Usage: python fetch_with_proxy.py <YOUTUBE_URL_OR_VIDEO_ID>")
        print("\nExample:")
        print('  python fetch_with_proxy.py "https://youtu.be/dQw4w9WgXcQ"')
        print('  python fetch_with_proxy.py dQw4w9WgXcQ')
        sys.exit(1)

    url_or_id = sys.argv[1]

    # Extract video ID
    video_id = extract_video_id(url_or_id)
    if not video_id:
        print(f"✗ Invalid YouTube URL or video ID: {url_or_id}")
        sys.exit(1)

    print(f"Fetching transcript for: {video_id}")

    # Initialize database
    init_db()

    # Setup proxy (index 2 works!)
    proxy_config = setup_proxy_from_file("proxies.txt", proxy_index=2)

    # Create session and orchestrator
    session_gen = get_session()
    session = next(session_gen)
    orchestrator = TranscriptOrchestrator(session=session, proxy_config=proxy_config)

    # Fetch transcript
    result = orchestrator.get_transcript(video_id)

    if result:
        print(f"\n✓ SUCCESS!")
        print(f"  Video ID: {result.video_id}")
        print(f"  Language: {result.language}")
        print(f"  Type: {result.transcript_type}")
        print(f"  Duration: {result.duration}s")
        print(f"\nTranscript:")
        print("-" * 80)
        print(result.transcript)
        print("-" * 80)
    else:
        print(f"\n✗ No transcript available for video: {video_id}")
        print("  This video might not have captions/subtitles enabled")
        sys.exit(1)

if __name__ == "__main__":
    main()
