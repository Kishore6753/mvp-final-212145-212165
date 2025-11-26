# Testing Strategy

## Overview
Testing ensures the backend reliably delivers the MVP journeys with auditability and traceability. The strategy spans unit, integration, contract, and data-validation tests, with seeded fixtures derived from canonical Excel sources.

## Unit Tests
- Gap calculation: verify correct interpretation of levels and ranges (e.g., P–A, A–Au).
- Plan generation: assert deterministic step sequencing and action types.
- Role adjacency: validate weight derivation using the min/max overlap method.

## Integration Tests
- Auth flows: register/login/logout round trips with JWT checks.
- End-to-end: select roles → submit assessment → gap → plan → export.
- Admin: template create/edit and audit-log retrieval (403 for non-admin).

## Contract Tests
- Validate endpoints conform to the interface schemas (request/response).
- Verify error model for invalid inputs and unknown IDs.

## Data Ingestion Tests
- Parse a minimal Competency_mapping.xlsx fixture; pivot to role_competency_map and assert row counts.
- Validate rejection of unknown roles and invalid tokens.
- Ensure import_batches and file_ingestions records are created with correct status.

## Observability and CI
- Each test logs traceIds for failure triage.
- CI runs unit and contract tests on PRs; integration tests run nightly with seeded fixtures.
