"""
api/health.py
-------------
Health & version endpoints.

Routes:
    GET /api/v1/health    — liveness + DB connectivity check
    GET /api/v1/version   — service version and runtime metadata
"""

from __future__ import annotations

import platform
import sys

from flask import Blueprint, current_app, jsonify

from schemas.health import HealthResponse, VersionResponse
from utils.logger import get_logger

logger = get_logger(__name__)
health_bp = Blueprint("health", __name__)


# ---------------------------------------------------------------------------
# GET /health
# ---------------------------------------------------------------------------

@health_bp.get("/health")
def health_check():
    """
    Liveness probe.

    Returns 200 when the service and database are healthy.
    Returns 503 when the database is unreachable.

    Response shape:
        {
            "status": "healthy",
            "service": "Program Management AI Assistant",
            "version": "1.0.0",
            "environment": "development",
            "database": { "status": "ok" }
        }
    """
    from database.db import health_check as db_health

    cfg        = current_app.config
    db_status  = db_health()
    is_healthy = db_status.get("status") == "ok"

    response = HealthResponse(
        status      = "healthy"  if is_healthy else "degraded",
        service     = cfg.get("SERVICE_NAME", "Program Management AI Assistant"),
        version     = cfg.get("APP_VERSION",  "1.0.0"),
        environment = cfg.get("ENVIRONMENT",  "unknown"),
        database    = db_status,
    )

    http_code = 200 if is_healthy else 503
    logger.debug("Health check → %s (db=%s)", response.status, db_status["status"])
    return jsonify(response.model_dump(exclude_none=True)), http_code


# ---------------------------------------------------------------------------
# GET /version
# ---------------------------------------------------------------------------

@health_bp.get("/version")
def version():
    """
    Service version and runtime information.

    Response shape:
        {
            "status": "success",
            "service": "Program Management AI Assistant",
            "version": "1.0.0",
            "environment": "development",
            "python_version": "3.12.8"
        }
    """
    cfg = current_app.config

    response = VersionResponse(
        status         = "success",
        service        = cfg.get("SERVICE_NAME", "Program Management AI Assistant"),
        version        = cfg.get("APP_VERSION",  "1.0.0"),
        environment    = cfg.get("ENVIRONMENT",  "unknown"),
        python_version = platform.python_version(),
    )

    logger.debug("Version requested → %s", response.version)
    return jsonify(response.model_dump(exclude_none=True)), 200
