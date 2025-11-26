
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from src.api.settings import adapt_db_url_for_driver, get_database_url

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
    first_line = msg.splitlines()[0] if msg else "unknown error"
    redactions = [
        "password",
        "user=",
        "username",
        "secret",
        "key",
        "token",
        "dsn",
        "url=",
        "uri",
        "@",  # often appears in DSNs like user:pass@host
    ]
    lowered = first_line.lower()
    for token in redactions:
        if token in lowered:
            return "database connection error"
    # trim overly long messages
    return first_line[:200]


def _get_engine() -> Tuple[Engine, Dict[str, Any]]:
    """
    Create a SQLAlchemy sync engine from the DATABASE_URL environment variable.

    Returns:
        (Engine, diagnostics) where diagnostics includes only non-sensitive hints.
    """
    db_url, diagnostics = get_database_url()
    adapted_url, adapt_diag = adapt_db_url_for_driver(db_url)
    diagnostics.update(adapt_diag)

    engine = create_engine(
        adapted_url,
        pool_pre_ping=True,  # validates connections are alive
        pool_size=1,
        max_overflow=0,
        future=True,
    )
    return engine, diagnostics


def _classify_exception(exc: Exception) -> str:
    """
    Map common failure modes to concise, sanitized messages.
    We avoid including secrets or raw DSNs.
    """
    msg = str(exc).lower()

    # Common categories
    if "could not translate host name" in msg or "getaddrinfo failed" in msg or "name or service not known" in msg:
        return "dns resolution error"
    if "connection refused" in msg or "timeout expired" in msg or "timed out" in msg:
        return "network connectivity error"
    if "ssl" in msg or "tls" in msg or "certificate" in msg:
        return "tls/ssl handshake error"
    if "password authentication failed" in msg or "authentication failed" in msg or "role" in msg:
        return "authentication error"
    if "psycopg2" in msg and "module not found" in msg:
        return "missing psycopg2 driver"
    if "psycopg" in msg and "module not found" in msg:
        return "missing psycopg driver"
    if "no module named" in msg and "psycopg" in msg:
        return "missing psycopg driver"
    if "server closed the connection unexpectedly" in msg:
        return "server connection closed"
    if "sslmode=required" in msg:
        return "ssl configuration error"

    # Fallback to masked message
    return _mask_error_message(str(exc))


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
        200: {"description": "Database connection OK", "content": {"application/json": {}}},
        503: {"description": "Database connection error", "content": {"application/json": {}}},
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
        engine, diag = _get_engine()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 as ok, current_database() as db, now() as ts"))
            row = result.first()
            if not row:
                raise RuntimeError("no result from database")

            db_name = str(getattr(row, "db", None)) if hasattr(row, "db") else None
            ts = getattr(row, "ts", None)
            iso_ts = ts.isoformat() if isinstance(ts, datetime) else (str(ts) if ts else None)

            return HealthDBResponse(status="ok", database=db_name, time=iso_ts)

    except Exception as exc:
        classified = _classify_exception(exc)

        # Append non-sensitive hints about configuration if relevant
        hint_parts = []
        try:
            # Best effort to read flags for hinting
            _, preflight = get_database_url()
            if not preflight.get("has_sslmode_require"):
                hint_parts.append("sslmode=require not found in DATABASE_URL")
            if not preflight.get("has_channel_binding"):
                hint_parts.append("channel_binding=require not found in DATABASE_URL")
        except Exception:
            # ignore hints if DATABASE_URL missing
            pass

        hint_suffix = f" ({'; '.join(hint_parts)})" if hint_parts else ""
        detail_msg = f"{classified}{hint_suffix}".strip()

        raise HTTPException(
            status_code=503,
            detail=HealthDBResponse(status="error", details=detail_msg).model_dump(),
        )
