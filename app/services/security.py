from __future__ import annotations

import ipaddress
import socket
from urllib.parse import urlparse


BLOCKED_HOSTNAMES = {"localhost", "localhost.localdomain"}
ALLOWED_SCHEMES = {"http", "https"}
ALLOWED_PORTS = {80, 443, None}


def _resolved_addresses(hostname: str) -> set[ipaddress.IPv4Address | ipaddress.IPv6Address]:
    addresses: set[ipaddress.IPv4Address | ipaddress.IPv6Address] = set()
    try:
        results = socket.getaddrinfo(hostname, None, type=socket.SOCK_STREAM)
    except (OSError, UnicodeError) as exc:
        raise ValueError("The target hostname could not be resolved.") from exc

    for result in results:
        address = result[4][0]
        try:
            addresses.add(ipaddress.ip_address(address))
        except ValueError as exc:
            raise ValueError("The target hostname returned an invalid IP address.") from exc
    return addresses


def validate_public_url(target: str, *, resolve_dns: bool = True) -> str:
    parsed = urlparse(target)
    if parsed.scheme.lower() not in ALLOWED_SCHEMES or not parsed.hostname:
        raise ValueError("Enter a valid HTTP(S) URL.")
    if parsed.username is not None or parsed.password is not None:
        raise ValueError("URLs containing embedded credentials are not allowed.")
    if parsed.port not in ALLOWED_PORTS:
        raise ValueError("Only standard HTTP and HTTPS ports are allowed.")

    hostname = parsed.hostname.rstrip(".").lower()
    if hostname in BLOCKED_HOSTNAMES or hostname.endswith(".localhost"):
        raise ValueError("Localhost targets are not allowed.")

    try:
        literal_ip = ipaddress.ip_address(hostname)
    except ValueError:
        literal_ip = None

    if literal_ip is not None:
        if not literal_ip.is_global:
            raise ValueError("Private, local, or reserved IP targets are not allowed.")
    elif resolve_dns:
        addresses = _resolved_addresses(hostname)
        if not addresses or any(not address.is_global for address in addresses):
            raise ValueError("The target hostname resolves to a private, local, or reserved address.")

    return target
