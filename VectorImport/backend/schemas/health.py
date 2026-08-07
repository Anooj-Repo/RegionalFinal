"""
schemas/health.py
-----------------
Pydantic schemas for the /health and /version endpoints.

These inherit from BaseResponse and define the exact payload shapes
returned by the Health API — no domain logic.
"""

from __future__ import annotations

from pydantic import Field

from schemas.base import BaseResponse


# ---------------------------------------------------------------------------
# /health
# ---------------------------------------------------------------------------

class DatabaseStatus(BaseResponse):
    """Nested database connectivity result inside HealthResponse."""

    model_config = {"populate_by_name": True}

    status: str = Field(..., examples=["ok", "error"])
    detail: str | None = Field(default=None)


class HealthResponse(BaseResponse):
    """
    Shape of GET /health.

    Example:
        {
            "status": "healthy",
            "service": "Program Management AI Assistant",
            "version": "1.0.0",
            "environment": "development",
            "database": { "status": "ok" }
        }
    """

    service: str = Field(
        ...,
        description="Human-readable service name.",
        examples=["Program Management AI Assistant"],
    )
    version: str = Field(
        ...,
        description="Semantic version of the running service.",
        examples=["1.0.0"],
    )
    environment: str = Field(
        ...,
        description="Deployment environment.",
        examples=["development", "production"],
    )
    database: dict = Field(
        default_factory=dict,
        description="Database connectivity status.",
    )


# ---------------------------------------------------------------------------
# /version
# ---------------------------------------------------------------------------

class VersionResponse(BaseResponse):
    """
    Shape of GET /version.

    Example:
        {
            "status": "success",
            "service": "Program Management AI Assistant",
            "version": "1.0.0",
            "environment": "development",
            "python_version": "3.12.8"
        }
    """

    service: str = Field(..., examples=["Program Management AI Assistant"])
    version: str = Field(..., examples=["1.0.0"])
    environment: str = Field(..., examples=["development"])
    python_version: str = Field(..., description="Python runtime version.")
