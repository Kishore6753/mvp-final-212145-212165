# Acceptance Criteria

## Executive Summary and Scope
The MVP supports a single-step career journey (e.g., Chief Architect → CTO), including role selection, competency self-assessment, gap analysis, development plan generation, and alternative role suggestions. Resume parsing, LinkedIn integration, coaching content, payments, and HR enablement are out of scope.

## Functional Criteria
1. Role selection: users can pick current and target roles from curated data.
2. Competency self-assessment: users can submit levels for canonical competencies.
3. Gap analysis: backend returns GapAnalysisResult with gaps and visualization data.
4. Development plan: backend returns a DevelopmentPlan with ordered steps and optional export link.
5. Adjacency: backend returns a list of alternative roles with weights/rationale.
6. Admin: templates can be created/edited; audit logs can be retrieved with authorization.

## Data and Integrity
- Competency ranges (P–A, A–Au) are correctly parsed and stored as min/max.
- Traceability is maintained from entities to source files and import batches.
- All writes generate audit log entries with user and entity context.

## Security and Compliance
- All protected endpoints require JWT; admin endpoints enforce role checks.
- Internal data access uses mTLS and internal service token.
- No sensitive tokens or PII are logged; errors return stable codes/messages.

## Operations
- Health check returns 200.
- Logging respects PGLOG_LEVEL.
- Environment variables PGPORT, PGTRUST_PROXY, PGLOG_LEVEL, PGHEALTHCHECK_PATH, PGFEATURE_FLAGS, PGEXPERIMENTS_ENABLED are read and effective.

## Non-Functional
- Endpoint responses adhere to interface schemas.
- Lists are paginated where applicable.
- P95 latency targets are documented for key endpoints (informational for MVP).
