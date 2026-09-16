# Internet X-Ray 🔎

> **Make the invisible parts of the web visible.**

Internet X-Ray loads a public URL in Chromium and turns browser/network activity into measurable evidence: request timing, resource mix, third-party hosts, failures, response sizes, security-header observations, and a visual request waterfall.

## Why it exists

A browser hides most of the work required to display a page. X-Ray exposes that work without pretending that a measurement is a diagnosis.

## Current capabilities

- Real Chromium capture with Playwright
- Redirect and final-URL detection
- Request/response status and failure tracking
- Resource-type and hostname breakdowns
- First-party vs third-party host detection
- Per-request start time and duration
- Response-size measurements when Chromium exposes them
- Navigation timing: DNS, TCP, TLS, TTFB, DOM ready, and load
- Security-header presence observations for five common headers
- Host dependency graph data in the API
- Browser-based request waterfall
- Responsive dashboard and API validation tests

## Architecture

```text
URL
 │
 ▼
FastAPI validation
 │
 ▼
Playwright / Chromium
 ├── request events
 ├── response events
 ├── failure events
 └── Performance Navigation Timing
 │
 ▼
Normalized analysis model
 ├── metrics
 ├── request stream
 ├── dependency graph
 └── security signals
 │
 ▼
Browser dashboard
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

Run tests with:

```bash
pytest
```

## Roadmap

- [x] Measurement layer
- [x] Request waterfall
- [x] Security-header observations
- [x] Failure reporting
- [x] Dependency graph data
- [ ] Interactive dependency graph
- [ ] Better DNS/TLS phase attribution per request
- [ ] Resource optimization insights
- [ ] Exportable JSON/HTML report
- [ ] Automated CI test suite
- [ ] Deployment

## Scope & safety

Designed for ordinary public HTTP(S) pages. Do not use it to bypass authentication, CAPTCHAs, paywalls, or access controls. Measurements can vary by network, browser, cache, geolocation, and target-server behavior.

## License

MIT
