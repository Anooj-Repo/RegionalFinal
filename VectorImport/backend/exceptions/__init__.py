"""
exceptions/__init__.py
-----------------------
Public surface of the exceptions package.

    from exceptions import ProjectNotFoundError, ValidationError, LLMConfigurationError
    from exceptions import register_error_handlers
"""

from exceptions.base import AppBaseError, ClientError, ServerError
from exceptions.domain import (
    AdapterError,
    AuthorizationError,
    DatabaseError,
    DocumentNotFoundError,
    GraphExecutionError,
    LLMConfigurationError,
    LLMError,
    ProjectNotFoundError,
    RAGError,
    ResourceNotFoundError,
    RiskNotFoundError,
    ValidationError,
)
from exceptions.handlers import register_error_handlers

__all__ = [
    # Base
    "AppBaseError",
    "ClientError",
    "ServerError",
    # Domain — client errors
    "ValidationError",
    "ResourceNotFoundError",
    "ProjectNotFoundError",
    "DocumentNotFoundError",
    "RiskNotFoundError",
    "AuthorizationError",
    # Domain — server errors
    "GraphExecutionError",
    "AdapterError",
    "RAGError",
    "DatabaseError",
    "LLMError",
    "LLMConfigurationError",
    # Registration
    "register_error_handlers",
]
