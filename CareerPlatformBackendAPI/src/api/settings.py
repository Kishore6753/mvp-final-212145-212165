"""Settings and environment configuration utilities for the FastAPI backend.

This module:
- Loads environment variables from the process environment and, if present, from a local .env file (without overriding existing env).
- Provides helpers to access and sanitize configuration (e.g., DATABASE_URL) without exposing secrets.
- Adapts the SQLAlchemy DB URL to prefer psycopg (psycopg3) if psycopg2 is unavailable.
- Logs a one-line, non-sensitive summary of DB config presence on app startup.
"""
import logging
import os
from importlib.util import find_spec
from typing import Any, Dict, Optional, Tuple

try:
    # python-dotenv is optional; use if available to load a .env file
    from dotenv import find_dotenv, load_dotenv
except Exception:  # pragma: no cover - optional dependency is already declared in requirements
    find_dotenv = None  # type: ignore
    load_dotenv = None  # type: ignore

_DOTENV_LOADED = False


def _load_dotenv_once() -> Optional[str]:
    """Load .env once if available and not yet loaded. Does not override existing os.environ values."""
    global _DOTENV_LOADED
    if _DOTENV_LOADED:
        return None

    _DOTENV_LOADED = True
    if not (find_dotenv and load_dotenv):
        return None

    path = find_dotenv(usecwd=True)
    if path and os.path.exists(path):
        # Do not override environment variables that the container/runtime has already provided.
        load_dotenv(dotenv_path=path, override=False)
        return path
    return None


# Load .env on module import (if present). Safe and idempotent.
_load_dotenv_once()


def _driver_segment_from_url(url: str) -> str:
    """Return the driver segment in the SQLAlchemy URL, or 'unspecified' if none."""
    lower = url.lower()
    if "+psycopg2" in lower:
        return "psycopg2"
    if "+psycopg" in lower:
        return "psycopg"
    return "unspecified"


# PUBLIC_INTERFACE
def get_database_url() -> Tuple[str, Dict[str, Any]]:
    """Get the DATABASE_URL from environment (optionally populated by .env if present).

    Returns:
        Tuple[str, Dict[str, Any]]: The database URL and a non-sensitive diagnostics map with flags:
            - has_sslmode_require: bool
            - has_channel_binding: bool
            - driver: 'psycopg' | 'psycopg2' | 'unspecified'

    Raises:
        RuntimeError: If DATABASE_URL is not configured.
    """
    _load_dotenv_once()
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        raise RuntimeError("DATABASE_URL is not configured")

    lower = db_url.lower()
    diag: Dict[str, Any] = {
        "has_sslmode_require": "sslmode=require" in lower,
        "has_channel_binding": ("channel_binding=require" in lower) or ("channel_binding=strict" in lower),
        "driver": _driver_segment_from_url(lower),
    }
    return db_url, diag


# PUBLIC_INTERFACE
def adapt_db_url_for_driver(db_url: str) -> Tuple[str, Dict[str, Any]]:
    """Ensure the DB URL is compatible with installed drivers, preferring psycopg (psycopg3) if psycopg2 is absent.

    If the URL explicitly requires psycopg2 but psycopg2 is not installed and psycopg is, replace +psycopg2 with +psycopg.
    If the URL does not specify a driver and psycopg2 is not installed while psycopg is available, add +psycopg.

    Args:
        db_url: The original database URL.

    Returns:
        Tuple[str, Dict[str, Any]]: (possibly adapted URL, adaptation diagnostics with keys:
            - driver_adapted: bool
            - selected_driver: 'psycopg' | 'psycopg2' | 'unspecified'
        )
    """
    diag: Dict[str, Any] = {"driver_adapted": False, "selected_driver": None}

    has_psycopg3 = find_spec("psycopg") is not None
    has_psycopg2 = find_spec("psycopg2") is not None

    adapted = db_url

    # If URL pins psycopg2 but it's not available, prefer psycopg (if available)
    if "+psycopg2" in db_url and not has_psycopg2 and has_psycopg3:
        adapted = db_url.replace("+psycopg2", "+psycopg")
        diag["driver_adapted"] = True
        diag["selected_driver"] = "psycopg"

    # If no explicit driver: add psycopg if psycopg2 is missing but psycopg exists
    elif ("+psycopg" not in db_url) and ("+psycopg2" not in db_url):
        if not has_psycopg2 and has_psycopg3:
            if db_url.startswith("postgresql://"):
                adapted = db_url.replace("postgresql://", "postgresql+psycopg://", 1)
            elif db_url.startswith("postgres://"):
                # 'postgres://' is commonly used; SQLAlchemy treats it as 'postgresql://'
                adapted = db_url.replace("postgres://", "postgresql+psycopg://", 1)
            # else: leave untouched if scheme is something else
            diag["driver_adapted"] = True
            diag["selected_driver"] = "psycopg"

    # If not previously set, infer selected driver from adapted URL
    lower = adapted.lower()
    if diag.get("selected_driver") is None:
        if "+psycopg2" in lower:
            diag["selected_driver"] = "psycopg2"
        elif "+psycopg" in lower:
            diag["selected_driver"] = "psycopg"
        else:
            diag["selected_driver"] = "unspecified"

    return adapted, diag


# PUBLIC_INTERFACE
def log_database_url_status(logger: Optional[logging.Logger] = None) -> None:
    """Log a one-line, sanitized indication of DATABASE_URL presence and key non-sensitive flags.

    The log omits secrets/DSN values and prints only booleans and driver hints.
    Intended to be called on application startup.

    Args:
        logger: Optional logger to use. Defaults to the 'uvicorn.error' logger.
    """
    log = logger or logging.getLogger("uvicorn.error")
    try:
        db_url, flags = get_database_url()
        adapted_url, adapt_info = adapt_db_url_for_driver(db_url)
        selected_driver = adapt_info.get("selected_driver") or flags.get("driver") or "unspecified"

        msg = (
            "CONFIG: DATABASE_URL detected; "
            f"driver={selected_driver}; "
            f"sslmode=require={str(flags.get('has_sslmode_require', False)).lower()}; "
            f"channel_binding={str(flags.get('has_channel_binding', False)).lower()}"
        )
        log.info(msg)
        # Fallback print if INFO level logs are filtered out by environment
        if not log.isEnabledFor(logging.INFO):
            print(msg)
    except Exception:
        msg = "CONFIG: DATABASE_URL not set; DB health checks will return 503 until configured."
        log.warning(msg)
        if not log.isEnabledFor(logging.WARNING):
            print(msg)
