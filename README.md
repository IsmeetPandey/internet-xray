# Internet X-Ray 🔎

> Make the invisible parts of the web visible.

Internet X-Ray is a web diagnostics tool that analyzes what happens after a user enters a URL: redirects, request timing, response metadata, resource types, and third-party domains.

## What this first version does

- Accepts a public HTTP(S) URL.
- Loads it in a real Chromium browser through Playwright.
- Captures network requests and responses.
- Reports status codes, resource types, transferred sizes when available, and timing.
- Detects redirects and groups requests by hostname.
- Highlights third-party hosts relative to the analyzed page.
- Serves a small browser UI from the same FastAPI application.

## Architecture

```text
Browser UI
    │
    ▼
FastAPI API
    │
    ▼
Playwright / Chromium
    │
    ├── Navigation events
    ├── Request/response events
    └── Page timing
    │
    ▼
Normalized analysis JSON
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

## Project direction

This repository is intentionally starting with a reliable measurement layer before adding heavier visualization and analysis features. Planned work includes a request graph, waterfall timeline, DNS/TLS breakdown, tracker classification, exportable reports, and performance comparisons.

## Safety / scope

Only analyze URLs you are authorized to access. The application is designed for ordinary public web pages and does not attempt to bypass authentication, CAPTCHAs, paywalls, or access controls.

## License

MIT
