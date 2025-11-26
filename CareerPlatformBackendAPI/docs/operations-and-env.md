# Operations and Environment

## Overview
This guide explains how to operate the backend service for the MVP Career Platform, including environment variables, health checks, and deployment notes.

## Environment Variables
The container reads the following variables:
- PGPORT: HTTP port the service should bind to.
- PGTRUST_PROXY: When “true”, trust reverse proxy headers for client IP.
- PGLOG_LEVEL: Log verbosity (e.g., info, debug, warn, error).
- PGHEALTHCHECK_PATH: Path for health checks (default “/” in MVP).
- PGFEATURE_FLAGS: Comma-separated feature toggles (e.g., “adjacency,export”).
- PGEXPERIMENTS_ENABLED: When “true”, allow experimental routes/features.

Values should be configured per environment (dev/stage/prod) and injected through the platform’s standard mechanism.

## Health and Readiness
- Liveness: GET ${PGHEALTHCHECK_PATH} returns 200 with a small JSON body.
- Readiness: same path for MVP; future versions may expose /readyz.
- OpenAPI: served under /docs when enabled by the runtime.

## Logging
- Structured JSON logs at PGLOG_LEVEL.
- Include requestId/traceId; never log sensitive tokens or PII.

## Deployment Notes
- Run behind a reverse proxy/ingress with HTTPS termination.
- Outbound calls to the internal data API require mTLS client certs and X-Internal-Token.

## Runbook (Incidents)
- 5xx spikes: capture sample traceIds; check dependency (database/internal API) health.
- Elevated 4xx: review auth and RBAC configuration; check token issuer settings.
- Import failures: inspect file_ingestions and import_batches for errors and retry counts.
