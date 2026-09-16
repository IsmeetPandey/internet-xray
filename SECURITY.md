# Security Policy

## Scope

Internet X-Ray is designed to inspect public HTTP(S) resources that a user is authorized to access.

## Reporting a security issue

Please do not publish sensitive vulnerability details in a public issue. Contact the repository owner privately through GitHub with:

- A short description of the issue
- Steps to reproduce, where safe to share
- The affected component or file
- Any suggested mitigation

## Safety boundaries

The application includes SSRF-aware URL validation and should not be used to bypass authentication, CAPTCHAs, paywalls, or other access controls. Production deployments should also apply network egress controls, rate limits, and appropriate resource limits.
