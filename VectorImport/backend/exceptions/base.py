"""
exceptions/base.py
------------------
Base exception hierarchy for the entire application.

All custom exceptions inherit from AppBaseError so callers
can catch everything with a single `except AppBaseError`.

Hierarchy:
    AppBaseError
    ├── ClientError      (4xx — caller's fault)
    └── ServerError      (5xx — our fault)
"""

from __future__ import annotations
from http import HTTPStatus


class AppBaseError(Exception):
    """
    Root of every custom exception in this application.

    Attributes:
        message:     Human-readable error description.
        http_status: HTTP status code to return to the client.
        code:        Machine-readable error code string (e.g. "NOT_FOUND").
        details:     Optional extra context for debugging / logging.
    """

    http_status: int = HTTPStatus.INTERNAL_SERVER_ERROR
    code: str        = "INTERNAL_ERROR"

    def __init__(
        self,
        message: str = "An unexpected error occurred.",
        details: dict | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def to_dict(self) -> dict:
        """Serialise to a dict suitable for a JSON error response."""
        payload: dict = {
            "status":  "error",
            "code":    self.code,
            "message": self.message,
        }
        if self.details:
            payload["details"] = self.details
        return payload

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(code={self.code!r}, message={self.message!r})"


# ---------------------------------------------------------------------------
# Broad categories
# ---------------------------------------------------------------------------

class ClientError(AppBaseError):
    """
    4xx — The client sent a bad request.
    The caller must fix the input; retrying unchanged will fail again.
    """
    http_status = HTTPStatus.BAD_REQUEST
    code        = "CLIENT_ERROR"


class ServerError(AppBaseError):
    """
    5xx — Something broke on our side.
    The caller can retry; we need to investigate.
    """
    http_status = HTTPStatus.INTERNAL_SERVER_ERROR
    code        = "SERVER_ERROR"
