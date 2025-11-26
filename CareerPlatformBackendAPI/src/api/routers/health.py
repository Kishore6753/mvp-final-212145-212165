import os
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

# We will use SQLAlchemy's sync engine for a minimal connection test.
# This avoids introducing async complexity if the rest of the app is sync.
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine


router = APIRouter(prefix="/health", tags=["Health"])


class HealthDBResponse(BaseModel):
    """Response schema for database health check."""

    status: str = Field(..., description='Connection status "ok" or "error"')
    database: Optional[str] = Field(None, description="Database name if available")
    time: Optional[str] = Field(None, description="Server time as ISO8601 if available")
    details: Optional[str] = Field(
        None,
        description="Non-sensitive diagnostic info on error. Avoids secrets.",
    )


def _mask_error_message(msg: str) -> str:
    """
    Mask potentially sensitive values like credentials in error messages.
    This is a simple heuristic; we avoid including the DATABASE_URL altogether.
    """
    # Avoid returning long or potentially sensitive messages
    # Keep only a short first line, strip any URLs.
    first_line = msg.splitlines()[0] if msg else "unknown error"
    # redact common tokens that might slip into messages
    redactions = ["password", "user", "username", "secret", "key", "token", "dsn", "url", "uri"]
    lowered = first_line.lower()
    for token in redactions:
        if token in lowered:
            return "database connection error"
    return first_line[:200]


def _get_engine() -> Engine:
    """
    Create a SQLAlchemy sync engine from the DATABASE_URL environment variable.
    Neon requires SSL; rely on sslmode=require within the provided URL. We do not
    hardcode credentials here.
    """
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        raise RuntimeError("DATABASE_URL is not configured")

    # Create a small-pool engine to minimize resource usage.
    return create_engine(
        db_url,
        pool_pre_ping=True,  # validates connections are alive
        pool_size=1,
        max_overflow=0,
        future=True,
    )


# PUBLIC_INTERFACE
@router.get(
    "/db",
    summary="Database connectivity health check",
    description="""
Checks connectivity to the configured PostgreSQL database using a lightweight query.

Usage:
- GET /api/v1/health/db

Successful response (200):
{
  "status": "ok",
  "database": "<db_name>",
  "time": "<server_time_iso8601>"
}

Failure response (503):
{
  "status": "error",
  "details": "<concise non-sensitive error>"
}
""",
    responses={
        200: {
            "description": "Database connection OK",
            "content": {"application/json": {}},
        },
        503: {
            "description": "Database connection error",
            "content": {"application/json": {}},
        },
    },
)
def health_check_db() -> HealthDBResponse:
    """
    Perform a simple DB connectivity check by executing 'SELECT 1, current_database(), now()'.
    Returns a sanitized response without exposing secrets.

    Returns:
        HealthDBResponse: status ok|error, with database and time fields when available.
    Raises:
        HTTPException: with 503 status code when the DB cannot be reached.
    """
    try:
        engine = _get_engine()
        with engine.connect() as conn:
            # Lightweight query for connectivity and basic metadata
            result = conn.execute(text("SELECT 1 as ok, current_database() as db, now() as ts"))
            row = result.first()
            if not row:
                raise RuntimeError("no result from database")

            # Build response
            db_name = str(row.db) if hasattr(row, "db") else None
            ts = row.ts if hasattr(row, "ts") else None
            iso_ts = ts.isoformat() if isinstance(ts, datetime) else (str(ts) if ts else None)

            return HealthDBResponse(status="ok", database=db_name, time=iso_ts)

    except Exception as exc:
        message = _mask_error_message(str(exc))
        # Return HTTP 503 without sensitive details
        raise HTTPException(status_code=503, detail=HealthDBResponse(status="error", details=message).model_dump())


# Note:
# - This router is safe for internal use and does not expose secrets.
# - It is isolated for easy removal later.
