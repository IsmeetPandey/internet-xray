# Internet X-Ray 🔎

> **Make the invisible parts of the web visible.**

Internet X-Ray loads a public URL in Chromium and turns browser/network activity into measurable evidence: request timing, resource mix, third-party hosts, failures, response sizes, security-header observations, dependency data, and exportable reports.

## What it does

- Captures a real Chromium page with Playwright.
- Tracks requests, responses, failures, resource types, hosts, timings, and sizes when available.
- Separates same-site and third-party traffic using hostname relationships.
- Measures navigation DNS, TCP, TLS, TTFB, DOM-ready, and load timings.
- Observes five common response security headers.
- Produces dependency-graph data for downstream visualization.
- Renders a browser request waterfall.
- Exports the current analysis as JSON or standalone HTML.
- Rejects non-HTTP(S), credential-bearing, non-standard-port, localhost, private, and reserved targets.

## Architecture

```text
URL
 │
 ▼
FastAPI validation + SSRF guard
 │
 ▼
Playwright / Chromium
 ├── request events
 ├── response events
 ├── failure events
 └── Navigation Timing API
 │
 ▼
Normalized analysis model
 ├── metrics
 ├── request stream
 ├── dependency graph
 └── security signals
 │
 ├── Browser dashboard
 └── JSON / HTML report export
```

## Run locally

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000`.

Run the test suite:

```bash
pytest -q
```

## API

- `GET /health` — service health check.
- `POST /api/analyze` — analyze a validated public URL.
- `POST /api/report/json` — wrap an analysis in the versioned JSON report format.
- `POST /api/report/html` — generate a standalone HTML report.

## Engineering notes

Measurements are observations, not diagnoses. Results vary with network conditions, browser version, cache state, geolocation, target-server behavior, and dynamically loaded content. The server validates navigation and browser subrequests, but production deployments should also run behind network egress controls and rate limiting.

## Roadmap

- [x] Measurement layer
- [x] Request waterfall
- [x] Security-header observations
- [x] Failure reporting
- [x] Dependency graph data
- [x] Exportable JSON/HTML reports
- [x] Automated CI test workflow
- [ ] Interactive dependency graph
- [ ] Per-request DNS/TLS phase attribution
- [ ] Resource optimization insights
- [ ] Production deployment and operational limits

## Scope & safety

Designed for ordinary public HTTP(S) pages. Do not use it to bypass authentication, CAPTCHAs, paywalls, or access controls. Measurements should be interpreted within their collection context.

## License

MIT
