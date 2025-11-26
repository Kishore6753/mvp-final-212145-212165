# Security and Compliance

## Overview
Security and compliance are enforced through layered controls in the backend service: JWT for external requests, mTLS and an internal token for backend↔database calls, strict input validation, and auditable evidence of all changes. The MVP emphasizes “risk-by-design” and “controls-as-code,” aligning with the program’s governance model.

## External Authentication (Frontend → Backend)
- Scheme: Bearer JWT in the Authorization header.
- Token verification: signature, expiry, issuer/audience as per org policy.
- Least privilege: endpoints require JWT except public auth endpoints.
- Error responses avoid sensitive specifics; traceIds are recorded in logs, not returned to the client beyond a stable string.

## Internal Authentication (Backend → Database/Internal API)
- mTLS is required to establish client identity.
- An internal service token is sent in the X-Internal-Token header.
- Backend service account is the only authorized client.

## Input Validation and Output Encoding
- Request bodies are validated against the interface schemas.
- All strings are length- and character-checked to prevent injection.
- Error payloads return stable codes and generic messages.

## Logging, Auditability, and Traceability
- Structured logs include timestamp, requestId/traceId, userId, action, latency, and outcome.
- Audit logs are written for every create/update/delete, including entityType, entityId, and initiating user where applicable.
- Traceability records link entities and mappings to source documents (Excel files) and import batches.

## Data Minimization and Privacy
- Store only what the MVP needs: roles, competencies, assessments, gaps, plans, and minimal profile attributes.
- Do not ingest resumes or LinkedIn profiles in the MVP.
- Navigator worksheet fields (interest, sponsorship) can be stored against a user with retention and purpose limits.

## Transport and At-Rest Security
- HTTPS for external clients to the backend.
- mTLS for backend↔internal API.
- Database encryption at rest per platform defaults; backups encrypted and access-controlled.

## Policy-as-Code and Risk-by-Design
- Thresholds (e.g., maximum plan steps, required completeness of assessment) are expressed as configuration and are auditable.
- Exceptions/waivers are time-limited and recorded with evidence.

## Administrative Access
- Admin-only endpoints (templates, audit-log) enforce role checks in addition to JWT validation.
- Administrative actions are always audited and monitored.
