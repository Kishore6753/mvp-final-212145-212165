# Backend ↔ Internal Database API

## Overview
This document specifies the internal API contract between the CareerPlatformBackendAPI (FastAPI) and the CareerPlatformDatabase internal service. It focuses on secure CRUD operations for canonical entities, audit log retrieval, and traceability resolution to source documents.

## Security
### Schemes
- Internal Token: Header X-Internal-Token: <token>
- Mutual TLS: Client certificates are required for the backend to connect to the internal DB API.

### Authorization
- Only the backend service account is authorized. No public access.
- All requests must include:
  - X-Internal-Token
  - mTLS-established client identity

## Base URL
- https://career-platform-internal-api.local

## Core Schemas
- Entity: { id: string, entityType: string, data: object }
- AuditLog: { timestamp: date-time, userId: string, action: string, entityType: string, entityId: string, details?: object }
- Traceability: { entityType: string, entityId: string, sourceDocuments: string[] }
- ErrorResponse: { status: string, error: string, details?: object }

## Endpoints
### List Entities
- GET /entities/{entityType}
- 200: Entity[]

### Create Entity
- POST /entities/{entityType}
- Body: Entity
- 201: Entity

### Get Entity
- GET /entities/{entityType}/{id}
- 200: Entity
- 404: ErrorResponse

### Update Entity
- PUT /entities/{entityType}/{id}
- Body: Entity
- 200: Entity
- 404: ErrorResponse

### Delete Entity
- DELETE /entities/{entityType}/{id}
- 204 No Content
- 404: ErrorResponse

### Audit Logs (admin)
- GET /audit/logs
- 200: AuditLog[]

### Traceability
- GET /traceability/{entityType}/{entityId}
- 200: Traceability

## Canonical Entity Types
- users
- profiles
- roles
- competencies
- role_competency_map
- assessments
- gap_results
- development_plans
- role_adjacency_edges
- templates
- audit_logs
- traceability
- file_ingestions
- import_batches

## Example Requests

### Create a Role
Request:
```json
POST /entities/roles
{
  "id": "cto",
  "entityType": "roles",
  "data": {
    "name": "Chief Technology Officer",
    "description": "Owns technology strategy and platform outcomes",
    "version": "2025-11-24",
    "source": "attachments/role_cards/"
  }
}
```
Response:
```json
201
{
  "id": "cto",
  "entityType": "roles",
  "data": { "...": "..." }
}
```

### Read Competency Mapping Traceability
Request:
GET /traceability/role_competency_map/cto
Response:
```json
{
  "entityType": "role_competency_map",
  "entityId": "cto",
  "sourceDocuments": [
    "attachments/20251126_145448_Competency_mapping.xlsx"
  ]
}
```

## Error Model
All error responses include a stable message and optional details. Backend must propagate a traceId in logs rather than over-the-wire.

## Notes
- Every write must generate an audit entry with the backend’s service identity and the acting user when relevant.
- Backend should cache read-only metadata such as competency definitions with short TTL.
