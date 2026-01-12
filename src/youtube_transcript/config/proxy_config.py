"""Proxy configuration for YouTube transcript API."""

import os
import logging
from typing import Optional

from youtube_transcript_api.proxies import WebshareProxyConfig, GenericProxyConfig

logger = logging.getLogger(__name__)


def get_proxy_config():
    """
    Get proxy configuration from environment variables.

    Supports two proxy types:
    1. WebShare rotating proxies (recommended)
    2. Generic HTTP/HTTPS proxies

    WebShare Environment Variables:
    - WEBSHARE_PROXY_USERNAME: WebShare proxy username
    - WEBSHARE_PROXY_PASSWORD: WebShare proxy password
    - WEBSHARE_PROXY_LOCATIONS: Optional comma-separated country codes (e.g., "US,CA,UK")
    - WEBSHARE_PROXY_RETRIES: Optional retry count when blocked (default: 10)

    Generic Proxy Environment Variables:
    - GENERIC_PROXY_HTTP_URL: HTTP proxy URL (e.g., "http://proxy.example.com:8080")
    - GENERIC_PROXY_HTTPS_URL: HTTPS proxy URL (e.g., "https://proxy.example.com:8080")

    Returns:
        WebshareProxyConfig or GenericProxyConfig if credentials set, None otherwise

    Example:
        >>> # WebShare rotating proxy
        >>> os.environ['WEBSHARE_PROXY_USERNAME'] = 'myuser'
        >>> os.environ['WEBSHARE_PROXY_PASSWORD'] = 'mypass'
        >>> config = get_proxy_config()
        >>>
        >>> # Generic proxy
        >>> os.environ['GENERIC_PROXY_HTTP_URL'] = 'http://proxy.example.com:8080'
        >>> config = get_proxy_config()
    """
    # Try WebShare first
    webshare_username = os.getenv('WEBSHARE_PROXY_USERNAME')
    webshare_password = os.getenv('WEBSHARE_PROXY_PASSWORD')

    if webshare_username and webshare_password:
        # Optional settings
        locations_str = os.getenv('WEBSHARE_PROXY_LOCATIONS')
        locations = None
        if locations_str:
            locations = [loc.strip() for loc in locations_str.split(',') if loc.strip()]

        retries_str = os.getenv('WEBSHARE_PROXY_RETRIES')
        retries = 10  # Default
        if retries_str:
            try:
                retries = int(retries_str)
            except ValueError:
                logger.warning(f"Invalid WEBSHARE_PROXY_RETRIES: {retries_str}, using default 10")
                retries = 10

        try:
            config = WebshareProxyConfig(
                proxy_username=webshare_username,
                proxy_password=webshare_password,
                filter_ip_locations=locations,
                retries_when_blocked=retries,
            )
            logger.info(f"WebShare rotating proxy configured (retries: {retries})")
            return config
        except Exception as e:
            logger.error(f"Failed to create WebShare proxy config: {e}")
            return None

    # Try generic proxy
    http_url = os.getenv('GENERIC_PROXY_HTTP_URL')
    https_url = os.getenv('GENERIC_PROXY_HTTPS_URL')

    if http_url or https_url:
        try:
            config = GenericProxyConfig(http_url=http_url, https_url=https_url)
            logger.info(f"Generic proxy configured (http: {bool(http_url)}, https: {bool(https_url)})")
            return config
        except Exception as e:
            logger.error(f"Failed to create generic proxy config: {e}")
            return None

    # No proxy configured
    logger.debug("No proxy configuration found in environment")
    return None


def load_proxies_from_file(filepath: str) -> list[dict]:
    """
    Load proxy credentials from a WebShare proxy list file.

    File format (one proxy per line):
        IP:PORT:USERNAME:PASSWORD

    Args:
        filepath: Path to proxy list file

    Returns:
        List of dicts with proxy information

    Example:
        >>> proxies = load_proxies_from_file("proxies.txt")
        >>> print(proxies[0])
        {'ip': '142.111.48.253', 'port': '7030', 'username': 'user', 'password': 'pass'}
    """
    proxies = []

    try:
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                parts = line.split(':')
                if len(parts) == 4:
                    proxies.append({
                        'ip': parts[0],
                        'port': parts[1],
                        'username': parts[2],
                        'password': parts[3],
                        'http_url': f"http://{parts[2]}:{parts[3]}@{parts[0]}:{parts[1]}",
                        'https_url': f"http://{parts[2]}:{parts[3]}@{parts[0]}:{parts[1]}",
                    })

        logger.info(f"Loaded {len(proxies)} proxies from {filepath}")
        return proxies

    except FileNotFoundError:
        logger.error(f"Proxy file not found: {filepath}")
        return []
    except Exception as e:
        logger.error(f"Error loading proxy file {filepath}: {e}")
        return []


def setup_proxy_from_file(filepath: str, proxy_index: int = 0) -> Optional[GenericProxyConfig]:
    """
    Setup generic proxy config from a WebShare proxy list file.

    Args:
        filepath: Path to proxy list file
        proxy_index: Which proxy to use from the list (default: 0 = first proxy)

    Returns:
        GenericProxyConfig if successful, None otherwise

    Example:
        >>> config = setup_proxy_from_file("proxies.txt", proxy_index=0)
        >>> fetcher = YouTubeTranscriptFetcher(proxy_config=config)
    """
    proxies = load_proxies_from_file(filepath)

    if not proxies:
        return None

    if proxy_index >= len(proxies):
        logger.error(f"Proxy index {proxy_index} out of range (only {len(proxies)} proxies loaded)")
        return None

    proxy = proxies[proxy_index]

    try:
        config = GenericProxyConfig(
            http_url=proxy['http_url'],
            https_url=proxy['https_url'],
        )
        logger.info(f"Configured proxy #{proxy_index}: {proxy['ip']}:{proxy['port']}")
        return config
    except Exception as e:
        logger.error(f"Failed to create proxy config: {e}")
        return None
