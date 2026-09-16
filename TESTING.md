# Testing Playbook

The project separates fast unit coverage from browser-backed behavior.

## Fast checks

Run the full Python test suite with:

```bash
pytest -q
```

Tests cover the analyzer model, API behavior, reporting, and validation boundaries.

## Browser-backed checks

Local browser execution requires Chromium to be installed for Playwright. CI should install the browser before running integration tests when those tests are enabled.

## What to test when changing the analyzer

When request capture changes, verify successful responses, failed requests, third-party host classification, timing fields, and report serialization. When URL validation changes, keep tests for localhost, private/reserved addresses, unsupported schemes, credentials, and non-standard ports.

## Regression principle

Prefer a small test that captures the behavior being changed over a broad snapshot. This keeps failures explainable and makes security-sensitive changes easier to review.
