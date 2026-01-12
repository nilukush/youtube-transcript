"""Configuration module for YouTube transcript fetcher."""

from youtube_transcript.config.proxy_config import (
    get_proxy_config,
    load_proxies_from_file,
    setup_proxy_from_file,
)

__all__ = ["get_proxy_config", "load_proxies_from_file", "setup_proxy_from_file"]
