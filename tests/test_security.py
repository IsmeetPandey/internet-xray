import pytest

from app.services.security import validate_public_url


def test_rejects_non_http_scheme():
    with pytest.raises(ValueError, match="valid HTTP\(S\) URL"):
        validate_public_url("ftp://example.com", resolve_dns=False)


def test_rejects_embedded_credentials():
    with pytest.raises(ValueError, match="embedded credentials"):
        validate_public_url("https://user:pass@example.com", resolve_dns=False)


def test_rejects_non_standard_port():
    with pytest.raises(ValueError, match="standard HTTP and HTTPS ports"):
        validate_public_url("https://example.com:8080", resolve_dns=False)


@pytest.mark.parametrize("url", [
    "http://localhost/",
    "http://127.0.0.1/",
    "http://10.0.0.5/",
    "http://192.168.1.10/",
    "http://172.16.0.10/",
    "http://[::1]/",
])
def test_rejects_local_or_private_ip_targets(url):
    with pytest.raises(ValueError, match="Private, local, or reserved"):
        validate_public_url(url, resolve_dns=False)


def test_allows_public_ip_literal():
    assert validate_public_url("https://8.8.8.8/", resolve_dns=False) == "https://8.8.8.8/"
