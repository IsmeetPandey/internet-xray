from __future__ import annotations

import time
from collections import Counter
from dataclasses import asdict, dataclass
from typing import Any
from urllib.parse import urlparse

from playwright.async_api import Browser, Page, async_playwright


@dataclass
class RequestRecord:
    url: str
    method: str
    status: int | None
    resource_type: str
    host: str
    is_third_party: bool
    duration_ms: float | None
    response_size: int | None


async def analyze_url(target: str, timeout_ms: int = 20_000) -> dict[str, Any]:
    parsed = urlparse(target)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("Enter a valid HTTP(S) URL.")

    page_origin_host = parsed.hostname or ""
    records: list[RequestRecord] = []
    started_at = time.perf_counter()

    async with async_playwright() as pw:
        browser: Browser = await pw.chromium.launch(headless=True)
        try:
            page: Page = await browser.new_page()
            pending: dict[int, float] = {}

            def request_started(request: Any) -> None:
                pending[id(request)] = time.perf_counter()

            async def response_received(response: Any) -> None:
                request = response.request
                start = pending.get(id(request))
                duration = (time.perf_counter() - start) * 1000 if start else None
                host = urlparse(request.url).hostname or ""
                size: int | None = None
                try:
                    headers = await response.all_headers()
                    length = headers.get("content-length")
                    if length and length.isdigit():
                        size = int(length)
                except Exception:
                    pass
                records.append(
                    RequestRecord(
                        url=request.url,
                        method=request.method,
                        status=response.status,
                        resource_type=request.resource_type,
                        host=host,
                        is_third_party=host.lower() != page_origin_host.lower(),
                        duration_ms=round(duration, 1) if duration is not None else None,
                        response_size=size,
                    )
                )

            page.on("request", request_started)
            page.on("response", response_received)

            response = await page.goto(target, wait_until="domcontentloaded", timeout=timeout_ms)
            try:
                await page.wait_for_load_state("load", timeout=timeout_ms)
            except Exception:
                pass

            navigation_status = response.status if response else None
            final_url = page.url

            timing = await page.evaluate(
                """() => {
                    const n = performance.getEntriesByType('navigation')[0];
                    if (!n) return null;
                    return {
                        dns_ms: Math.max(0, n.domainLookupEnd - n.domainLookupStart),
                        tcp_ms: Math.max(0, n.connectEnd - n.connectStart),
                        tls_ms: n.secureConnectionStart ? Math.max(0, n.connectEnd - n.secureConnectionStart) : 0,
                        ttfb_ms: Math.max(0, n.responseStart - n.requestStart),
                        dom_content_loaded_ms: Math.max(0, n.domContentLoadedEventEnd - n.startTime),
                        load_event_ms: Math.max(0, n.loadEventEnd - n.startTime),
                        transfer_size: n.transferSize || null
                    };
                }"""
            )
        finally:
            await browser.close()

    total_ms = round((time.perf_counter() - started_at) * 1000, 1)
    resource_counts = Counter(r.resource_type for r in records)
    host_counts = Counter(r.host for r in records)
    third_party_hosts = sorted({r.host for r in records if r.is_third_party and r.host})
    total_known_bytes = sum(r.response_size or 0 for r in records)

    return {
        "requested_url": target,
        "final_url": final_url,
        "origin_host": page_origin_host,
        "navigation_status": navigation_status,
        "analysis_duration_ms": total_ms,
        "request_count": len(records),
        "third_party_request_count": sum(r.is_third_party for r in records),
        "third_party_hosts": third_party_hosts,
        "known_response_bytes": total_known_bytes,
        "resource_counts": dict(resource_counts),
        "host_counts": dict(host_counts.most_common()),
        "timing": timing,
        "requests": [asdict(r) for r in records],
    }
