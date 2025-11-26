# Project Repository

This is the initial README file for the project.

## Backend Health/DB Check

The CareerPlatformBackendAPI exposes a DB connectivity check endpoint.

- Method: GET
- Path: `/api/v1/health/db`
- Description: Executes a lightweight query against the configured Neon PostgreSQL database to verify connectivity. It returns only non-sensitive metadata.

Example success response (HTTP 200):
```
{
  "status": "ok",
  "database": "career_platform_db",
  "time": "2025-01-01T12:34:56.789012+00:00"
}
```

Example error response (HTTP 503):
```
{
  "status": "error",
  "details": "database connection error"
}
```

Notes:
- Configure the environment variable `DATABASE_URL` (should include `sslmode=require` for Neon).
- No secrets are logged or returned by this endpoint.