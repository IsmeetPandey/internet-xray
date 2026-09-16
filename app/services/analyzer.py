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
    start_ms: float | None
    duration_ms: float | None
    response_size: int | None
    failed: bool
    failure: str | None


def _same_site(host: str, origin_host: str) -> bool:
    host = host.lower().strip(".")
    origin_host = origin_host.lower().strip(".")
    return bool(host and origin_host and (host == origin_host or host.endswith("." + origin_host) or origin_host.endswith("." + host)))


async def analyze_url(target: str, timeout_ms: int = 20_000) -> dict[str, Any]:
    parsed = urlparse(target)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("Enter a valid HTTP(S) URL.")

    origin_host = parsed.hostname or ""
    records: list[RequestRecord] = []
    started_at = time.perf_counter()
    navigation_status: int | None = None
    final_url = target
    main_headers: dict[str, str] = {}
    timing: dict[str, Any] | None = None
    page_title = ""

    async with async_playwright() as pw:
        browser: Browser = await pw.chromium.launch(headless=True)
        try:
            page: Page = await browser.new_page(viewport={"width": 1440, "height": 900})
            pending: dict[int, float] = {}

            def request_started(request: Any) -> None:
                pending[id(request)] = time.perf_counter()

            async def request_finished(request: Any) -> None:
                start_clock = pending.pop(id(request), None)
                response = await request.response()
                host = urlparse(request.url).hostname or ""
                status = response.status if response else None
                response_size: int | None = None
                failed = False
                failure = None
                if response:
                    try:
                        sizes = await request.sizes()
                        response_size = sizes.get("responseBodySize") or None
                    except Exception:
                        pass
                else:
                    failed = True
                    failure = request.failure or "request failed"
                resource_timing = request.timing
                start_ms = resource_timing.get("startTime") if resource_timing else None
                end_ms = resource_timing.get("responseEnd") if resource_timing else None
                duration = (end_ms - start_ms) if start_ms is not None and end_ms is not None and end_ms >= 0 else ((time.perf_counter() - start_clock) * 1000 if start_clock is not None else None)
                records.append(RequestRecord(
                    url=request.url,
                    method=request.method,
                    status=status,
                    resource_type=request.resource_type,
                    host=host,
                    is_third_party=not _same_site(host, origin_host),
                    start_ms=round(start_ms, 1) if start_ms is not None else None,
                    duration_ms=round(max(0.0, duration), 1) if duration is not None else None,
                    response_size=response_size,
                    failed=failed,
                    failure=failure,
                ))

            async def request_failed(request: Any) -> None:
                start_clock = pending.pop(id(request), None)
                host = urlparse(request.url).hostname or ""
                failure = request.failure or "request failed"
                duration = (time.perf_counter() - start_clock) * 1000 if start_clock is not None else None
                records.append(RequestRecord(
                    url=request.url,
                    method=request.method,
                    status=None,
                    resource_type=request.resource_type,
                    host=host,
                    is_third_party=not _same_site(host, origin_host),
                    start_ms=None,
                    duration_ms=round(duration, 1) if duration is not None else None,
                    response_size=None,
                    failed=True,
                    failure=failure,
                ))

            async def response_seen(response: Any) -> None:
                nonlocal navigation_status, main_headers
                if response.request.resource_type == "document":
                    navigation_status = response.status
                    try:
                        main_headers = await response.all_headers()
                    except Exception:
                        main_headers = {}

            page.on("request", request_started)
            page.on("requestfinished", request_finished)
            page.on("requestfailed", request_failed)
            page.on("response", response_seen)

            response = await page.goto(target, wait_until="domcontentloaded", timeout=timeout_ms)
            if response:
                navigation_status = response.status
                try:
                    main_headers = await response.all_headers()
                except Exception:
                    main_headers = {}
            try:
                await page.wait_for_load_state("load", timeout=timeout_ms)
            except Exception:
                pass
            await page.wait_for_timeout(250)

            final_url = page.url
            page_title = await page.title()
            timing = await page.evaluate("""() => {
                const n = performance.getEntriesByType('navigation')[0];
                if (!n) return null;
                return {
                    dns_ms: Math.max(0, n.domainLookupEnd - n.domainLookupStart),
                    tcp_ms: Math.max(0, n.connectEnd - n.connectStart),
                    tls_ms: n.secureConnectionStart > 0 ? Math.max(0, n.connectEnd - n.secureConnectionStart) : 0,
                    ttfb_ms: Math.max(0, n.responseStart - n.requestStart),
                    dom_content_loaded_ms: Math.max(0, n.domContentLoadedEventEnd - n.startTime),
                    load_event_ms: Math.max(0, n.loadEventEnd - n.startTime),
                    transfer_size: n.transferSize || 0,
                    encoded_body_size: n.encodedBodySize || 0,
                    decoded_body_size: n.decodedBodySize || 0
                };
            }""")
        finally:
            await browser.close()

    total_ms = round((time.perf_counter() - started_at) * 1000, 1)
    records.sort(key=lambda item: (item.start_ms if item.start_ms is not None else float("inf")))
    resource_counts = Counter(r.resource_type for r in records)
    host_counts = Counter(r.host for r in records if r.host)
    third_party_hosts = sorted({r.host for r in records if r.is_third_party and r.host})
    failed_requests = [r for r in records if r.failed]
    total_known_bytes = sum(r.response_size or 0 for r in records)
    timing = timing or {}
    header_names = (
        "content-security-policy",
        "strict-transport-security",
        "x-content-type-options",
        "referrer-policy",
        "permissions-policy",
    )
    security_headers = {name: main_headers.get(name) for name in header_names if main_headers.get(name)}
    missing_security_headers = [name for name in header_names if not main_headers.get(name)]

    # A compact host dependency graph: each observed host is linked to the page origin.
    # This describes network dependencies; it does not claim that one host caused another.
    dependency_nodes = sorted({origin_host, *[r.host for r in records if r.host]})
    dependency_edges = [
        {"source": origin_host, "target": host, "requests": count}
        for host, count in host_counts.items()
        if host and host != origin_host
    ]

    return {
        "requested_url": target,
        "final_url": final_url,
        "page_title": page_title,
        "origin_host": origin_host,
        "navigation_status": navigation_status,
        "analysis_duration_ms": total_ms,
        "request_count": len(records),
        "failed_request_count": len(failed_requests),
        "third_party_request_count": sum(r.is_third_party for r in records),
        "third_party_hosts": third_party_hosts,
        "known_response_bytes": total_known_bytes,
        "resource_counts": dict(resource_counts),
        "host_counts": dict(host_counts.most_common()),
        "timing": timing,
        "security_headers": security_headers,
        "missing_security_headers": missing_security_headers,
        "dependency_graph": {"nodes": dependency_nodes, "edges": dependency_edges},
        "requests": [asdict(r) for r in records],
    }
