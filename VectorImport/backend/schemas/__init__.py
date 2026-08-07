"""
schemas/__init__.py
-------------------
Public surface of the schemas package.

    from schemas import BaseResponse, BaseEntity, BaseTimestampModel
    from schemas import HealthResponse, VersionResponse
    from schemas.domain import ProjectSchema, RiskEntrySchema, ...
"""

from schemas.base import BaseEntity, BaseResponse, BaseTimestampModel
from schemas.health import HealthResponse, VersionResponse

__all__ = [
    # Base classes
    "BaseResponse",
    "BaseTimestampModel",
    "BaseEntity",
    # Health / version
    "HealthResponse",
    "VersionResponse",
    # Domain schemas are imported directly from schemas.domain
]
