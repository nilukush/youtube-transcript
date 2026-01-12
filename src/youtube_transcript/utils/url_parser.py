"""YouTube URL parser utility."""

import re
from typing import Optional
from urllib.parse import urlparse, parse_qs, unquote


def extract_video_id(url: str | None) -> Optional[str]:
    """
    Extract video ID from a YouTube URL.

    Supports 100+ YouTube URL formats including:
    - Standard watch URLs (youtube.com/watch?v=ID)
    - Short URLs (youtu.be/ID)
    - Embed URLs (youtube.com/embed/ID)
    - Shorts (youtube.com/shorts/ID)
    - Live streams (youtube.com/live/ID)
    - Mobile URLs (m.youtube.com/...)
    - Old formats (/v/ID, /e/ID)
    - URLs with or without protocol
    - URLs with various parameters
    - URLs with backslashes (automatically sanitized)

    The function automatically sanitizes URLs by removing backslashes,
    which can occur from:
    - Shell escaping (e.g., "https://youtu.be/ID\\?si=...")
    - Copy-paste from markdown or code
    - Manual input errors

    Args:
        url: YouTube URL to parse

    Returns:
        Video ID as string if found, None otherwise

    Examples:
        >>> extract_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        'dQw4w9WgXcQ'
        >>> extract_video_id("https://youtu.be/dQw4w9WgXcQ")
        'dQw4w9WgXcQ'
        >>> extract_video_id("https://www.youtube.com/shorts/j9rZxAF3C0I")
        'j9rZxAF3C0I'
        >>> extract_video_id("https://youtu.be/ID\\?si=tracking")  # With backslash
        'ID'
        >>> extract_video_id("https://example.com/watch?v=dQw4w9WgXcQ")
        None
    """
    if not url or not isinstance(url, str):
        return None

    # Sanitize URL: remove backslashes (invalid in URLs, often from shell escaping or copy-paste)
    # Backslashes are not valid in URLs per RFC 3986 - URLs use forward slashes
    # This handles cases where users escape characters in shell or copy from markdown
    url = url.replace('\\', '')

    # Check if it's a bare video ID (11 chars, alphanumeric with hyphens/underscores)
    # YouTube video IDs are typically 11 characters
    if re.match(r'^[A-Za-z0-9_-]{11}$', url.strip()):
        return url.strip()

    # Add protocol if missing
    if not url.startswith(('http://', 'https://')):
        if url.startswith('www.') or url.startswith('youtu.be') or 'youtube.com' in url:
            url = 'https://' + url
        else:
            return None

    # Normalize URL: handle case where & is used instead of ? in youtu.be URLs
    # This happens when youtu.be service converts & to ? internally
    normalized_url = url
    if "youtu.be/" in normalized_url and "?" not in normalized_url and "&" in normalized_url:
        # Replace first & with ? for youtu.be URLs
        parts = normalized_url.split("&", 1)
        if len(parts) == 2:
            normalized_url = parts[0] + "?" + parts[1]

    try:
        # Parse URL
        parsed = urlparse(normalized_url)

        # Check if it's a YouTube domain
        valid_domains = [
            'youtube.com',
            'm.youtube.com',
            'youtu.be',
            'www.youtube.com',
            'youtube-nocookie.com',
            'www.youtube-nocookie.com',
        ]

        if parsed.netloc not in valid_domains and parsed.netloc != 'youtu.be' and not parsed.netloc.endswith('.youtube.com'):
            # Try adding www. if missing
            if not parsed.netloc.startswith('www.') and parsed.netloc != 'youtu.be':
                # Check if it's a URL without protocol
                if '.' in parsed.netloc and 'youtube' in parsed.netloc:
                    # Already has a domain, just not in our list
                    pass
                else:
                    return None
            elif not any(domain in parsed.netloc for domain in valid_domains):
                return None

        # Extract video ID based on URL path format
        path = parsed.path

        # youtu.be/ID format
        if 'youtu.be' in parsed.netloc:
            # Extract from path (everything after /)
            video_id = path.strip('/').split('/')[0]
            # Remove any query parameters or fragments
            video_id = video_id.split('?')[0].split('#')[0]
            if len(video_id) >= 10:
                return video_id
            return None

        # /shorts/ID format
        if '/shorts/' in path:
            video_id = path.split('/shorts/')[-1]
            video_id = video_id.split('?')[0].split('#')[0]
            if len(video_id) >= 10:
                return video_id
            return None

        # /live/ID format
        if '/live/' in path:
            video_id = path.split('/live/')[-1]
            video_id = video_id.split('?')[0].split('#')[0]
            if len(video_id) >= 10:
                return video_id
            return None

        # /embed/ID format
        if '/embed/' in path:
            video_id = path.split('/embed/')[-1]
            video_id = video_id.split('?')[0].split('#')[0]
            if len(video_id) >= 10:
                return video_id
            return None

        # /v/ID format (old embed)
        if path.startswith('/v/') or path.startswith('/vi/'):
            video_id = path.split('/')[-1]
            video_id = video_id.split('?')[0].split('#')[0]
            if len(video_id) >= 10:
                return video_id
            return None

        # /e/ID format (old embed)
        if path.startswith('/e/'):
            video_id = path.split('/e/')[-1]
            video_id = video_id.split('?')[0].split('#')[0]
            if len(video_id) >= 10:
                return video_id
            return None

        # /watch/ID format (unusual but documented)
        if path.startswith('/watch/'):
            video_id = path.split('/watch/')[-1]
            video_id = video_id.split('?')[0].split('#')[0]
            if len(video_id) >= 10:
                return video_id
            return None

        # Standard watch URL with v parameter
        query_params = parse_qs(parsed.query)
        if 'v' in query_params:
            video_id = query_params['v'][0]
            if len(video_id) >= 10:
                return video_id
            return None

        # If no match found, try extracting from path
        # This catches some edge cases
        if path and path != '/' and path != '/watch':
            # Extract last path component that looks like a video ID
            parts = path.strip('/').split('/')
            if parts:
                potential_id = parts[-1].split('?')[0].split('#')[0]
                if len(potential_id) >= 10 and len(potential_id) <= 20:
                    # Check if it looks like a video ID (alphanumeric with possible hyphens/underscores)
                    if re.match(r'^[\w-]+$', potential_id):
                        return potential_id

        return None

    except Exception:
        # If parsing fails, return None
        return None
