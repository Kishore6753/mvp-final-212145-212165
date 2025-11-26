# Data Ingestion from Excel

## Overview
The MVP ingests three canonical Excel sources:
1) Competency_mapping.xlsx (wide format: competency rows, role columns)
2) CA_Role_Adjacency.xlsx (gaps/overlap basis, used to derive adjacency and rationale)
3) Role_Navigator_Worksheet.xlsx (personalization fields such as interest and sponsorship)

All ingestions must produce import batches, per-file ingestion records, and row-level validation outcomes, with traceability back to the original file and sheet coordinates.

## Source 1: Competency_mapping.xlsx
### Structure
- Header row includes: “Competency”, then role codes/headers such as “CA”, “CTO”, “BU CIO”, “CSO”, “COO”, “CoS”, “GSSO”, “CPO”, “CISO”, “CIO”, “CPTO”, “CDO”, “CTrO”, “CInO”, “CDAO”, “CAIO”, “PMO”, “AppDev”, “Infra”, “Ops”, “DigProd”, “FCTO”, “CCTO”, “VE”, “CP”.
- Cell values are proficiency levels or ranges: F, P, A, Au, P–A, A–Au.

### Mapping
- For each row:
  - Find or create competency by name.
  - For each role column with a non-empty value:
    - Parse the level or range into (min_level, max_level).
    - Upsert role_competency_map(role_id, competency_id, required_min_level, required_max_level).
- Create a traceability record linking role_competency_map entries to the file path and batch ID.

### Validation
- Unknown role header → error.
- Invalid level token → error (only F|P|A|Au|P–A|A–Au allowed).
- Duplicate competency names → error (unless explicitly permitted).
- At least one role column must be populated per competency.

### Example
Row: “Strategy-to-Capability” → CTO = “A”
- Insert: role_competency_map(“cto”, “strategy_to_capability”, min=A, max=A)

Row: “Enterprise Architecture” → CTO = “P–A”
- Insert: role_competency_map(“cto”, “enterprise_architecture”, min=P, max=A)

## Source 2: CA_Role_Adjacency.xlsx
### Structure (excerpt)
Rows list target role, canonical competency, and a “Gap (levels)” versus Chief Architect. Example gaps:
- Executive/board storytelling (internal): 1 (A → Au)
- Portfolio capital allocation & FinOps/Chargeback: 0.5 (P–A → A or A–Au)

### Overlap and Weights
- Per-competency overlap = min(level_i, level_j)/max(level_i, level_j).
- Overall overlap = mean across competencies with values in both roles.
- Weight = normalized overlap (e.g., 0.0–1.0). Persist in role_adjacency_edges(from_role, to_role, weight, rationale).

### Rationale
- Persist a brief rationale per edge combining top 2–3 differentiating competencies (highest gaps) for transparency.

## Source 3: Role_Navigator_Worksheet.xlsx
### Columns
- Interest (1–5), Overlap with Chief Architect (%), Sponsorship Strength (0–5), Readiness Runway (months), Risk/Regulatory Fit (0–5), Market Pull (0–5), Scope Appetite Fit (0–5), Notes/Evidence links.

### Mapping
- Store as a per-user preference document (or profile extension) keyed by userId and roleId. Attach navigator inputs to a GapAnalysisResult or plan as context to support conversation with a coach/sponsor.

## Versioning and Audit
- import_batches: one per import run; include source and timestamp.
- file_ingestions: one per file; include checksum, status, and errors.
- audit_logs: record who initiated imports and summarize counts (inserted/updated/failed).
- traceability: add origin file path and file row/column offsets for each created mapping.

## Suggested Pipeline Stages
1. Load file bytes and compute checksum.
2. Parse headers and validate tokens.
3. Upsert roles and competencies.
4. Populate role_competency_map.
5. Compute adjacency weights and persist edges.
6. Write batch/file ingestion records, including validation errors.

## Example Validation Errors
```json
[
  { "row": 18, "column": "CIO", "error": "Invalid level token 'AAu'" },
  { "row": 29, "column": "CTO", "error": "Unknown role header 'CTO (AI)'" }
]
```
