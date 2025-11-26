# User Journeys

## Overview
This document captures the primary user journeys supported by the backend, aligned to the MVP scope validated in the working session. The MVP delivers a single-step career move (e.g., Chief Architect to CTO), a structured gap analysis, a development plan, and adjacency-based alternative roles. Resume parsing, LinkedIn integration, and rich coaching content are explicitly out of scope for the MVP.

## Personas
### Technology Leader (primary)
A user who selects their current role and a target role, enters a simple competency self-assessment, and receives a plan.

### Admin (secondary)
A user who reviews audit logs and manages plan templates.

## Happy Path: Chief Architect → CTO
### Pre-conditions
- Curated roles and canonical competencies imported from Excel.
- The user is authenticated (JWT).

### Steps
1. Frontend requests role lists and displays a constrained dropdown for current and target roles.
2. User selects “Chief Architect” as current and “CTO” as target.
3. Frontend fetches canonical competencies for the target and renders a small self-assessment form.
4. User submits their current levels.
5. Backend computes gaps against CTO required levels and returns GapAnalysisResult.
6. Backend generates a DevelopmentPlan from the gaps and returns the plan.
7. User views plan and optionally requests an export link.

### Inputs and Outputs
- Input: currentRoleId, targetRoleId, currentCompetencies[]
- Output: GapAnalysisResult { gaps[], visualization{} }, DevelopmentPlan { steps[], actions[], exportLink? }

### Errors and Recovery
- Validation failure: return structured error with code and message; frontend highlights invalid fields.
- Unknown role: 404 Not Found.
- Inconsistent competency IDs: 400 Bad Request with a list of missing IDs.

## Alternative Role Suggestions (Adjacency)
### Steps
1. After gap analysis, backend computes or fetches adjacency candidates for the current role.
2. Returns a list of roles with weights and optional rationale.
3. Frontend displays suggestions (e.g., CISO, BU CIO) as secondary options.

### Inputs and Outputs
- Input: userId or currentRoleId
- Output: array of Role with adjacency weights and rationale

## Admin Journeys
### View Audit Logs
- Admin calls GET /api/v1/audit-logs and receives a paginated list of actions with timestamps and traceIds.

### Manage Templates
- Admin creates/edits plan templates via POST /api/v1/templates.

## ASCII Flow (Happy Path)
```
[User]
  |
  | Select roles + submit assessment
  v
[Frontend UI] --JWT--> [Backend API]
                          |
                          | fetch canonical target levels
                          v
                   [Internal Data API/DB]
                          |
                          v
                  compute gaps + plan
                          |
                          v
[Backend API] --results--> [Frontend UI] --> display plan / export
```

## Non-Happy Paths
- Missing assessment input: return 400 with “details” listing which competencies are missing.
- Plan generation failure: return 500; record audit log with error details and traceId for triage.
- Unauthorized admin call: return 403 Forbidden.
