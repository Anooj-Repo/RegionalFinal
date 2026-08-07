"""
schemas/base.py
---------------
Reusable Pydantic v2 base models.

These are the ONLY classes defined here — no domain/business models yet.
All future request/response schemas will inherit from one of these three.

Classes:
    BaseResponse        — standard API envelope (status + optional data/errors)
    BaseEntity          — base for any DB-backed resource (adds id field)
    BaseTimestampModel  — mixin that adds created_at / updated_at fields
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

# Generic type parameter used by BaseResponse[T]
DataT = TypeVar("DataT")


# ---------------------------------------------------------------------------
# 1. BaseResponse
# ---------------------------------------------------------------------------

class BaseResponse(BaseModel, Generic[DataT]):
    """
    Standard envelope for every API response.

    Usage — success:
        return BaseResponse[ProjectSchema](
            status="success",
            message="Project created.",
            data=project_schema,
        ).model_dump()

    Usage — error:
        return BaseResponse(
            status="error",
            message="Not found.",
            errors=["Project 42 does not exist."],
        ).model_dump(), 404

    Usage — plain (no data):
        return BaseResponse(status="healthy", message="Service is up.").model_dump()
    """

    model_config = ConfigDict(
        populate_by_name=True,   # allow field aliases
        str_strip_whitespace=True,
    )

    status: str = Field(
        ...,
        description="High-level result: 'success' | 'error' | 'healthy' | etc.",
        examples=["success", "error", "healthy"],
    )
    message: str | None = Field(
        default=None,
        description="Human-readable summary of the response.",
    )
    data: DataT | None = Field(
        default=None,
        description="Response payload — type depends on the endpoint.",
    )
    errors: list[str] | None = Field(
        default=None,
        description="List of error strings (populated only on failure).",
    )
    meta: dict[str, Any] | None = Field(
        default=None,
        description="Optional metadata (pagination, timing, etc.).",
    )


# ---------------------------------------------------------------------------
# 2. BaseTimestampModel
# ---------------------------------------------------------------------------

class BaseTimestampModel(BaseModel):
    """
    Mixin that adds read-only timestamp fields for DB-backed resources.

    Inherit alongside BaseEntity when you need created_at / updated_at
    in your response schema.

    Note: `from_attributes = True` allows direct construction from
    SQLAlchemy ORM instances via `MySchema.model_validate(orm_obj)`.
    """

    model_config = ConfigDict(
        from_attributes=True,      # ORM → Pydantic via model_validate()
        populate_by_name=True,
        str_strip_whitespace=True,
    )

    created_at: datetime | None = Field(
        default=None,
        description="UTC timestamp of record creation.",
    )
    updated_at: datetime | None = Field(
        default=None,
        description="UTC timestamp of last update.",
    )


# ---------------------------------------------------------------------------
# 3. BaseEntity
# ---------------------------------------------------------------------------

class BaseEntity(BaseTimestampModel):
    """
    Base for any schema that represents a DB-backed entity.

    Inherits BaseTimestampModel (created_at, updated_at) and adds `id`.

    All future domain schemas (ProjectSchema, DocumentSchema, etc.)
    will inherit from this class.

    Example:
        class ProjectSchema(BaseEntity):
            name: str
            status: str
    """

    id: int = Field(
        ...,
        description="Primary key of the database record.",
        examples=[1, 42, 1000],
        gt=0,
    )
