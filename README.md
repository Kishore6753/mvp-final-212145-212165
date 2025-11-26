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
- Configure the environment variable `DATABASE_URL` for Neon. It must include at minimum:
  - `sslmode=require`
  - `channel_binding=require` (or `channel_binding=strict`)
- Example (do NOT paste real secrets; this is illustrative): `postgresql://<user>:<password>@<host>.neon.tech/<db>?sslmode=require&channel_binding=require`
- Drivers:
  - The service supports psycopg3 (psycopg[binary]) and psycopg2-binary. If `+psycopg2` was embedded in the URL and the driver is unavailable, the health check will attempt to adapt to `+psycopg`.
- Troubleshooting:
  - 503 with `dns resolution error`: verify the hostname and network egress.
  - 503 with `tls/ssl handshake error`: confirm `sslmode=require` and TLS reachability.
  - 503 with `authentication error`: validate user/password and that the role exists in Neon.
  - 503 with `network connectivity error`: check firewall/VPC and outbound access.
- Security: No secrets are logged or returned by this endpoint.