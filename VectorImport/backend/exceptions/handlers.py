"""
exceptions/handlers.py
-----------------------
Flask global error handlers.

Registered once inside create_app() via register_error_handlers(app).

All responses follow the standard BaseResponse envelope:
    {
        "status":  "error",
        "code":    "PROJECT_NOT_FOUND",
        "message": "Project '42' was not found.",
        "details": {}          ← only in DEBUG mode
    }
"""

from __future__ import annotations

from flask import Flask, jsonify, current_app
from werkzeug.exceptions import HTTPException

from exceptions.base import AppBaseError
from utils.logger import get_logger

logger = get_logger(__name__)


def register_error_handlers(app: Flask) -> None:
    """
    Attach all global error handlers to the Flask app.
    Called once by the Application Factory.
    """

    # ── 1. Our own custom exceptions ────────────────────────────────────────
    @app.errorhandler(AppBaseError)
    def handle_app_error(exc: AppBaseError):
        """Handles every exception that inherits from AppBaseError."""
        logger.warning(
            "AppError [%s] %s — %s",
            exc.http_status,
            exc.code,
            exc.message,
        )

        payload = exc.to_dict()

        # Only expose internal details in DEBUG mode
        if not current_app.debug and "details" in payload:
            del payload["details"]

        return jsonify(payload), exc.http_status

    # ── 2. Werkzeug / Flask HTTP errors (404, 405, etc.) ────────────────────
    @app.errorhandler(HTTPException)
    def handle_http_exception(exc: HTTPException):
        """Converts Werkzeug HTTPExceptions to the standard JSON envelope."""
        logger.info("HTTPException [%s] %s", exc.code, exc.description)
        return jsonify({
            "status":  "error",
            "code":    exc.name.upper().replace(" ", "_"),
            "message": exc.description,
        }), exc.code

    # ── 3. Catch-all — unhandled Python exceptions ───────────────────────────
    @app.errorhandler(Exception)
    def handle_generic_exception(exc: Exception):
        """
        Safety net for any exception that slips through.
        Always returns 500 and never leaks stack traces in production.
        """
        logger.exception("Unhandled exception: %s", exc)

        payload: dict = {
            "status":  "error",
            "code":    "INTERNAL_ERROR",
            "message": "An unexpected internal error occurred.",
        }

        # Expose the raw error only in DEBUG mode
        if current_app.debug:
            payload["detail"] = str(exc)

        return jsonify(payload), 500
