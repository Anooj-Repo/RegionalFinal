"""
exceptions/domain.py
--------------------
Domain-specific exception classes.

Each exception maps to a specific layer of the application
and carries its own HTTP status code + machine-readable code.

Hierarchy (inherits from base.py):
    AppBaseError
    ├── ClientError
    │   ├── ValidationError
    │   ├── ProjectNotFoundError
    │   └── ResourceNotFoundError
    └── ServerError
        ├── GraphExecutionError
        ├── AdapterError
        └── RAGError
"""

from __future__ import annotations

from http import HTTPStatus

from exceptions.base import ClientError, ServerError


# ---------------------------------------------------------------------------
# Client-side errors  (4xx)
# ---------------------------------------------------------------------------

class ValidationError(ClientError):
    """
    Raised when incoming request data fails validation.

    HTTP 422 Unprocessable Entity.

    Example:
        raise ValidationError(
            message="'start_date' must be before 'end_date'.",
            field="start_date",
        )
    """

    http_status = HTTPStatus.UNPROCESSABLE_ENTITY
    code        = "VALIDATION_ERROR"

    def __init__(
        self,
        message: str = "Request validation failed.",
        field: str | None = None,
        details: dict | None = None,
    ) -> None:
        extra = details or {}
        if field:
            extra["field"] = field
        super().__init__(message=message, details=extra)


class ResourceNotFoundError(ClientError):
    """
    Generic 404 — a requested resource could not be found.

    HTTP 404 Not Found.
    """

    http_status = HTTPStatus.NOT_FOUND
    code        = "NOT_FOUND"

    def __init__(
        self,
        resource: str = "Resource",
        identifier: int | str | None = None,
        details: dict | None = None,
    ) -> None:
        id_part = f" '{identifier}'" if identifier is not None else ""
        message = f"{resource}{id_part} was not found."
        super().__init__(message=message, details=details)


class ProjectNotFoundError(ResourceNotFoundError):
    """
    Raised when a requested project does not exist in the database.

    HTTP 404 Not Found.

    Example:
        raise ProjectNotFoundError(project_id=42)
    """

    code = "PROJECT_NOT_FOUND"

    def __init__(
        self,
        project_id: int | str | None = None,
        details: dict | None = None,
    ) -> None:
        super().__init__(
            resource="Project",
            identifier=project_id,
            details=details,
        )


class DocumentNotFoundError(ResourceNotFoundError):
    """Raised when a requested document does not exist."""

    code = "DOCUMENT_NOT_FOUND"

    def __init__(self, document_id: int | str | None = None, details: dict | None = None) -> None:
        super().__init__(resource="Document", identifier=document_id, details=details)


class RiskNotFoundError(ResourceNotFoundError):
    """Raised when a requested risk record does not exist."""

    code = "RISK_NOT_FOUND"

    def __init__(self, risk_id: int | str | None = None, details: dict | None = None) -> None:
        super().__init__(resource="Risk", identifier=risk_id, details=details)


class AuthorizationError(ClientError):
    """
    Raised when a caller lacks permission for an action.

    HTTP 403 Forbidden.
    """

    http_status = HTTPStatus.FORBIDDEN
    code        = "FORBIDDEN"

    def __init__(
        self,
        message: str = "You do not have permission to perform this action.",
        details: dict | None = None,
    ) -> None:
        super().__init__(message=message, details=details)


# ---------------------------------------------------------------------------
# Server-side errors  (5xx)
# ---------------------------------------------------------------------------

class GraphExecutionError(ServerError):
    """
    Raised when a LangGraph workflow fails during execution.

    HTTP 500 Internal Server Error.

    Example:
        raise GraphExecutionError(
            graph_name="risk_analysis_graph",
            message="Node 'classify_risks' timed out.",
        )
    """

    code = "GRAPH_EXECUTION_ERROR"

    def __init__(
        self,
        message: str = "Workflow graph execution failed.",
        graph_name: str | None = None,
        details: dict | None = None,
    ) -> None:
        extra = details or {}
        if graph_name:
            extra["graph"] = graph_name
        super().__init__(message=message, details=extra)


class AdapterError(ServerError):
    """
    Raised when an external system adapter fails.

    HTTP 502 Bad Gateway — indicates an upstream system problem.

    Example:
        raise AdapterError(
            adapter="JiraAdapter",
            message="Connection refused.",
        )
    """

    http_status = HTTPStatus.BAD_GATEWAY
    code        = "ADAPTER_ERROR"

    def __init__(
        self,
        message: str = "External adapter call failed.",
        adapter: str | None = None,
        details: dict | None = None,
    ) -> None:
        extra = details or {}
        if adapter:
            extra["adapter"] = adapter
        super().__init__(message=message, details=extra)


class RAGError(ServerError):
    """
    Raised when the RAG (Retrieval-Augmented Generation) pipeline fails.

    HTTP 500 Internal Server Error.

    Example:
        raise RAGError(
            message="Vector store query returned 0 results unexpectedly.",
            stage="retrieval",
        )
    """

    code = "RAG_ERROR"

    def __init__(
        self,
        message: str = "RAG pipeline encountered an error.",
        stage: str | None = None,
        details: dict | None = None,
    ) -> None:
        extra = details or {}
        if stage:
            extra["stage"] = stage
        super().__init__(message=message, details=extra)


class DatabaseError(ServerError):
    """
    Raised when a database operation fails unexpectedly.

    HTTP 500 Internal Server Error.
    """

    code = "DATABASE_ERROR"

    def __init__(
        self,
        message: str = "A database error occurred.",
        details: dict | None = None,
    ) -> None:
        super().__init__(message=message, details=details)


class LLMError(ServerError):
    """
    Raised when an LLM service call fails.

    HTTP 500 Internal Server Error.
    """

    code = "LLM_ERROR"

    def __init__(
        self,
        message: str = "LLM service call failed.",
        details: dict | None = None,
    ) -> None:
        super().__init__(message=message, details=details)


class LLMConfigurationError(LLMError):
    """
    Raised when mandatory LLM credentials (LLM_API_KEY) are missing or invalid.

    HTTP 500 Internal Server Error.
    """

    code = "LLM_CONFIGURATION_ERROR"

    def __init__(
        self,
        message: str = "Required LLM API key is missing or not configured.",
        details: dict | None = None,
    ) -> None:
        super().__init__(message=message, details=details)

