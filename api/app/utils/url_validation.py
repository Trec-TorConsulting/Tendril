"""URL validation utilities to prevent SSRF attacks."""
from __future__ import annotations

import ipaddress
import socket
from urllib.parse import urlparse

from fastapi import HTTPException


# RFC 1918 and other private/reserved ranges that should never be fetched
_BLOCKED_NETWORKS = [
    ipaddress.ip_network("0.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("100.64.0.0/10"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.0.0.0/24"),
    ipaddress.ip_network("192.0.2.0/24"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("198.18.0.0/15"),
    ipaddress.ip_network("198.51.100.0/24"),
    ipaddress.ip_network("203.0.113.0/24"),
    ipaddress.ip_network("224.0.0.0/4"),
    ipaddress.ip_network("240.0.0.0/4"),
    ipaddress.ip_network("255.255.255.255/32"),
    # IPv6 private ranges
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),
    ipaddress.ip_network("fe80::/10"),
]

_ALLOWED_SCHEMES = {"http", "https", "rtsp"}


def _is_private_ip(ip_str: str) -> bool:
    """Check if an IP address falls within a blocked/private range."""
    try:
        addr = ipaddress.ip_address(ip_str)
    except ValueError:
        return True  # If we can't parse it, block it
    return any(addr in net for net in _BLOCKED_NETWORKS)


def validate_url_safe(url: str, *, allow_private: bool = False) -> str:
    """Validate that a URL is safe to fetch (no SSRF).

    Args:
        url: The URL to validate.
        allow_private: If True, skip private IP checks (for trusted internal use).

    Returns:
        The validated URL string.

    Raises:
        HTTPException: If the URL is unsafe.
    """
    parsed = urlparse(url)

    if parsed.scheme not in _ALLOWED_SCHEMES:
        raise HTTPException(
            status_code=400,
            detail=f"URL scheme '{parsed.scheme}' not allowed. Use http, https, or rtsp.",
        )

    hostname = parsed.hostname
    if not hostname:
        raise HTTPException(status_code=400, detail="URL must include a hostname.")

    if not allow_private:
        # Resolve hostname to IP to catch DNS rebinding
        try:
            resolved = socket.getaddrinfo(hostname, None, socket.AF_UNSPEC, socket.SOCK_STREAM)
        except socket.gaierror:
            raise HTTPException(status_code=400, detail=f"Cannot resolve hostname: {hostname}")

        for family, _type, _proto, _canonname, sockaddr in resolved:
            ip_str = sockaddr[0]
            if _is_private_ip(ip_str):
                raise HTTPException(
                    status_code=400,
                    detail="URL must not point to a private or reserved IP address.",
                )

    return url
