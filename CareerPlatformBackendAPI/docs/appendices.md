# Appendices

## Consolidated API Catalog (Frontend ↔ Backend)
- Auth: POST /api/v1/auth/register, /auth/login, /auth/logout, /auth/reset-password
- Profile: GET/PUT /api/v1/profile
- Roles and Competencies: GET /api/v1/roles, GET /api/v1/competencies
- Selection/Assessment: POST /api/v1/roles/select, POST /api/v1/competencies/assess
- Gap Analysis: POST /api/v1/gap-analysis
- Development Plan: POST /api/v1/development-plan, GET /api/v1/development-plan/export
- Role Adjacency: GET /api/v1/role-adjacency
- Admin: GET /api/v1/audit-logs, GET/POST /api/v1/templates

## Consolidated Internal API (Backend ↔ Database)
- Entities CRUD: /entities/{entityType}[GET, POST], /entities/{entityType}/{id}[GET, PUT, DELETE]
- Audit logs: GET /audit/logs
- Traceability: GET /traceability/{entityType}/{entityId}

## Data Dictionary (Selected)
- Proficiency Level: { F, P, A, Au }; Range tokens: “P–A”, “A–Au”.
- role_competency_map.required_min_level: enum(F,P,A,Au)
- role_competency_map.required_max_level: enum(F,P,A,Au)
- role_adjacency_edges.weight: float(0..1), computed via mean overlap.
- assessment_items.level: enum(F,P,A,Au)
- gap_items.current_level, required_min_level, required_max_level: enum(F,P,A,Au)

## Excel-to-DB Mapping (Summary)
- Competency_mapping.xlsx → role_competency_map (pivot columns per role)
- CA_Role_Adjacency.xlsx → role_adjacency_edges (weight) + rationale
- Role_Navigator_Worksheet.xlsx → user preference context attached to gap/plan

## Example Payloads
### Gap Analysis Request
```json
{
  "currentCompetencies": [
    { "id": "enterprise_architecture", "name": "Enterprise Architecture", "proficiencyLevel": "P" }
  ],
  "targetRoleId": "cto"
}
```

### Development Plan (Excerpt)
```json
{
  "steps": [
    { "description": "Elevate board storytelling to A→Au", "actionType": "practice", "resource": "Exec storytelling deck" }
  ],
  "actions": ["schedule sponsor review", "track outcomes in KPI sheet"],
  "context": "Chief Architect → CTO"
}
```
