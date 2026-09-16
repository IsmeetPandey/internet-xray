import asyncio

import pytest

from app.services.analyzer import _same_site, analyze_url
from app.services.security import validate_public_url


def test_analyze_url_rejects_non_http_scheme():
    with pytest.raises(ValueError, match=r"valid HTTP\(S\) URL"):
        asyncio.run(analyze_url("ftp://example.com"))


def test_same_site_handles_subdomains():
    assert _same_site("cdn.example.com", "example.com")
    assert not _same_site("example.net", "example.com")


@pytest.mark.parametrize("url", [
    "http://localhost",
    "http://127.0.0.1",
    "http://192.168.1.10",
    "https://example.com:8080",
    "https://user:pass@example.com",
])
def test_public_url_guard_rejects_unsafe_targets(url):
    with pytest.raises(ValueError):
        validate_public_url(url, resolve_dns=False)
