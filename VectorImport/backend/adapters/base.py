"""
adapters/base.py
----------------
Abstract base class for every data-source adapter.

Contract:
    Every adapter exposes exactly ONE public method:

        load(project_id: int) -> T

    Return type T is typed in the subclass — never a plain dict.

Subclasses MUST:
    1. Override `load()` and return fully-validated Pydantic models.
    2. Call `self._validate()` before returning.
    3. Log errors via self._log.
    4. Raise AdapterError on failure.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from exceptions import AdapterError
from utils.logger import get_logger

T = TypeVar("T")


class BaseAdapter(ABC, Generic[T]):
    """
    Generic abstract adapter.

    Usage:
        class MyAdapter(BaseAdapter[list[MySchema]]):
            def load(self, project_id: int) -> list[MySchema]:
                ...
    """

    # Subclasses set this to identify themselves in logs/errors.
    adapter_name: str = "BaseAdapter"

    def __init__(self) -> None:
        self._log: logging.Logger = get_logger(
            f"adapters.{self.adapter_name}"
        )

    @abstractmethod
    def load(self, project_id: int) -> T:
        """
        Load and return typed domain data for the given project.

        Args:
            project_id: Integer primary key of the project.

        Returns:
            Fully-validated Pydantic model(s). Never a raw dict.

        Raises:
            AdapterError: If data cannot be loaded or validated.
        """
        ...

    # ── Protected helpers ────────────────────────────────────────────────────

    def _raise(self, message: str, cause: Exception | None = None) -> None:
        """Wrap any exception into a typed AdapterError and raise it."""
        self._log.error("[%s] %s — cause: %s", self.adapter_name, message, cause)
        raise AdapterError(
            message=message,
            adapter=self.adapter_name,
            details={"cause": str(cause)} if cause else {},
        ) from cause

    def _validate(self, models: list) -> list:
        """
        Ensure every item in a list is a Pydantic model (not a dict).
        Raises AssertionError immediately if the contract is violated.
        """
        for item in models:
            assert hasattr(type(item), "model_fields"), (
                f"{self.adapter_name}.load() must return Pydantic models, "
                f"got {type(item).__name__}"
            )
        return models
