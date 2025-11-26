# Frontend ↔ Backend API Catalog

## Overview
This catalog lists the REST endpoints exposed by the backend for the frontend, including auth requirements, request/response schemas, and sample payloads based on the OpenAPI spec.

## Authentication
- Scheme: Bearer JWT (Authorization: Bearer <token>)
- Public: /auth/register, /auth/login, /auth/reset-password (as applicable)
- Protected: All other endpoints

## Endpoints

### Auth
- POST /api/v1/auth/register
  - Request: User
  - Response: 201 User
- POST /api/v1/auth/login
  - Request: { email, password }
  - Response: { token }
- POST /api/v1/auth/logout
  - Response: 204
- POST /api/v1/auth/reset-password
  - Request: { email }
  - Response: 200

Example login:
```json
POST /api/v1/auth/login
{
  "email": "user@example.com",
  "password": "Passw0rd!"
}
```
Response:
```json
200
{ "token": "eyJhbGciOi..." }
```

### Profile
- GET /api/v1/profile
  - Response: Profile
- PUT /api/v1/profile
  - Request: Profile
  - Response: 200 Profile

### Roles and Competencies
- GET /api/v1/roles
  - Response: [Role]
- POST /api/v1/roles/select
  - Request: { currentRoleId, targetRoleId }
  - Response: 200
- GET /api/v1/competencies
  - Response: [Competency]
- POST /api/v1/competencies/assess
  - Request: [Competency]
  - Response: 200

Sample role:
```json
{
  "id": "cto",
  "name": "Chief Technology Officer",
  "description": "Owns technology strategy and platform outcomes",
  "competencies": [
    { "id": "strategy_to_capability", "name": "Strategy-to-Capability", "definition": "Translate strategy...", "proficiencyLevel": "A" }
  ]
}
```

### Gap Analysis and Development Plan
- POST /api/v1/gap-analysis
  - Request: { currentCompetencies: [Competency], targetRoleId: string }
  - Response: GapAnalysisResult
- POST /api/v1/development-plan
  - Request: GapAnalysisResult
  - Response: DevelopmentPlan
- GET /api/v1/development-plan/export
  - Response: { exportLink }

Example gap analysis request:
```json
{
  "currentCompetencies": [
    { "id": "enterprise_architecture", "name": "Enterprise Architecture", "proficiencyLevel": "P" }
  ],
  "targetRoleId": "cto"
}
```
Response (excerpt):
```json
{
  "gaps": [
    { "id": "platform_economics", "name": "Platform Economics", "proficiencyLevel": "A" }
  ]
}
```

### Role Adjacency
- GET /api/v1/role-adjacency
  - Response: [Role] (suggested alternatives)

### Admin
- GET /api/v1/audit-logs
  - Response: [AuditLog]
- GET /api/v1/templates
  - Response: [Template]
- POST /api/v1/templates
  - Request: Template
  - Response: Template

## Error Model
- Default error schema:
```json
{ "code": "string", "message": "string", "traceId": "string" }
```

## Notes
- The generated OpenAPI is available at interfaces/openapi.json and /docs at runtime.
- JWT issuance and validation should align with organization signing keys and rotation practices.

Sources: 
- interfaces/openapi.json
- src/api/main.py
