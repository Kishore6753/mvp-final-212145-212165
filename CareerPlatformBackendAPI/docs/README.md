# Career Platform Backend API – Documentation

## Overview
This documentation set covers the MVP Career Platform’s backend service built with FastAPI. It describes scope, architecture, APIs, modules, data flows, security, testing, operations, and acceptance criteria.

## Contents
- architecture.md — System architecture, data flow, security, logging, and compliance
- apis-frontend-backend.md — Frontend ↔ Backend REST API catalog, auth, schemas, examples
- apis-internal-db.md — Backend ↔ Database internal API catalog, security (internal token, mTLS)
- modules-and-schema.md — Service decomposition and proposed database schema (ERD-level)
- frontend-components.md — (Cross-reference to the Web Frontend docs)
- user-journeys.md — User flows and touchpoints
- d3-graphs.md — Role map graph model and D3 rendering approach
- data-ingestion-from-excel.md — Excel ingestion strategy and canonical tables
- security-and-compliance.md — JWT, RBAC, PII, encryption-in-transit, auditability
- testing-strategy.md — Unit, integration, contract testing, seeded fixtures
- operations-and-env.md — Environment variables, health checks, runbook basics
- acceptance-criteria.md — MVP criteria and readiness checklist
- appendices.md — Consolidated endpoints, data dictionary, Excel-to-DB mappings

## Related Containers
- CareerPlatformWebFrontend (React): see its docs/ for UI components, routing, and D3.
- CareerPlatformDatabase (PostgreSQL): see its docs/ for schema, operations, and internal API.

## Source References
- src/api/main.py
- interfaces/openapi.json (generated)
- requirements.txt

