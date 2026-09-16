# Operations Notes

Internet X-Ray is intended to inspect ordinary public HTTP(S) pages. A production deployment should treat the service as an active browser workload.

## Resource controls

Use request timeouts, concurrency limits, rate limiting, and bounded report sizes. Chromium processes can consume significant CPU and memory, so deployments should cap concurrent analyses.

## Network controls

Keep application-level URL validation enabled and add outbound firewall/egress policy at the infrastructure layer. DNS results and redirects should remain within the deployment's intended policy.

## Observability

Useful operational signals include analysis duration, timeout/failure counts, browser launch failures, request counts, and report-generation errors. Logs should avoid recording secrets or sensitive URL query parameters unnecessarily.

## Failure handling

A target website can fail independently of the service. Reports should preserve the distinction between target-side failures, browser/network failures, and application validation errors so operators can troubleshoot the correct layer.
