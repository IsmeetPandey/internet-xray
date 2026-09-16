from app.services.analyzer import analyze_url


def test_analyze_url_rejects_non_http_scheme():
    import pytest

    with pytest.raises(ValueError, match="valid HTTP\(S\) URL"):
        import asyncio
        asyncio.run(analyze_url("ftp://example.com"))
