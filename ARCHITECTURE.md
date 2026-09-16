# Architecture Notes

Internet X-Ray is organized as a measurement pipeline rather than a single monolithic request handler.

## Flow

1. **Input validation** — the API validates the submitted URL and rejects unsupported or unsafe targets.
2. **Browser capture** — Playwright drives Chromium and records request, response, and failure events.
3. **Navigation timing** — browser timing data is collected to add DNS, TCP, TLS, TTFB, DOM-ready, and load observations when available.
4. **Normalization** — raw browser events are converted into a stable analysis model containing metrics, requests, dependencies, failures, and security signals.
5. **Presentation** — the dashboard and report endpoints consume the same normalized model instead of re-running the capture.

## Design boundaries

The analyzer should remain focused on evidence collection. Interpretation belongs in the reporting/presentation layer so that measurements can be inspected independently.

The SSRF guard is deliberately applied before navigation. Production deployments should also enforce network egress controls because application-level validation is only one layer of defense.

## Extension points

Future changes can add per-request DNS/TLS attribution, interactive dependency visualization, and resource optimization insights without changing the basic capture pipeline.
