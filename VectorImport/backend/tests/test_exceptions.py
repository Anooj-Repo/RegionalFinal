"""
tests/test_exceptions.py
------------------------
Tests for the custom exception hierarchy and the Flask global error handlers.
"""

import pytest
from http import HTTPStatus


# ---------------------------------------------------------------------------
# Exception class unit tests
# ---------------------------------------------------------------------------

class TestExceptionHierarchy:

    def test_app_base_error_defaults(self):
        from exceptions import AppBaseError
        e = AppBaseError()
        assert e.http_status == 500
        assert e.code == "INTERNAL_ERROR"
        assert "unexpected" in e.message.lower()

    def test_app_base_error_to_dict(self):
        from exceptions import AppBaseError
        e = AppBaseError(message="boom", details={"key": "val"})
        d = e.to_dict()
        assert d["status"] == "error"
        assert d["code"] == "INTERNAL_ERROR"
        assert d["message"] == "boom"
        assert d["details"] == {"key": "val"}

    def test_project_not_found_message(self):
        from exceptions import ProjectNotFoundError
        e = ProjectNotFoundError(project_id=42)
        assert "42" in e.message
        assert e.http_status == 404
        assert e.code == "PROJECT_NOT_FOUND"

    def test_project_not_found_no_id(self):
        from exceptions import ProjectNotFoundError
        e = ProjectNotFoundError()
        assert e.http_status == 404

    def test_validation_error_with_field(self):
        from exceptions import ValidationError
        e = ValidationError(message="Invalid date.", field="start_date")
        assert e.http_status == 422
        assert e.code == "VALIDATION_ERROR"
        assert e.details["field"] == "start_date"

    def test_graph_execution_error(self):
        from exceptions import GraphExecutionError
        e = GraphExecutionError(graph_name="risk_graph", message="Timeout.")
        assert e.http_status == 500
        assert e.code == "GRAPH_EXECUTION_ERROR"
        assert e.details["graph"] == "risk_graph"

    def test_adapter_error_status(self):
        from exceptions import AdapterError
        e = AdapterError(adapter="JiraAdapter")
        assert e.http_status == 502
        assert e.code == "ADAPTER_ERROR"
        assert e.details["adapter"] == "JiraAdapter"

    def test_rag_error(self):
        from exceptions import RAGError
        e = RAGError(stage="retrieval", message="No vectors found.")
        assert e.http_status == 500
        assert e.code == "RAG_ERROR"
        assert e.details["stage"] == "retrieval"

    def test_client_error_is_subclass_of_base(self):
        from exceptions import ProjectNotFoundError, AppBaseError, ClientError
        e = ProjectNotFoundError()
        assert isinstance(e, AppBaseError)
        assert isinstance(e, ClientError)

    def test_server_error_is_subclass_of_base(self):
        from exceptions import GraphExecutionError, AppBaseError, ServerError
        e = GraphExecutionError()
        assert isinstance(e, AppBaseError)
        assert isinstance(e, ServerError)


# ---------------------------------------------------------------------------
# Flask global error handler integration tests
# ---------------------------------------------------------------------------

# Pre-register all error-trigger routes as a Blueprint.
# This must happen before the first request (Flask 3.x constraint).
from flask import Blueprint as _Blueprint

_error_bp = _Blueprint("error_tests", __name__)

@_error_bp.get("/test/project-not-found")
def _project_not_found():
    from exceptions import ProjectNotFoundError
    raise ProjectNotFoundError(project_id=99)

@_error_bp.get("/test/validation-error")
def _validation_error():
    from exceptions import ValidationError
    raise ValidationError(message="Bad field.", field="name")

@_error_bp.get("/test/adapter-error")
def _adapter_error():
    from exceptions import AdapterError
    raise AdapterError(adapter="MockAdapter")

@_error_bp.get("/test/unhandled")
def _unhandled():
    raise RuntimeError("Something totally unexpected.")


class TestErrorHandlers:

    @classmethod
    @pytest.fixture(autouse=True, scope="class")
    def register_test_routes(cls, app):
        """Register the error-trigger blueprint once before any request."""
        if "error_tests" not in app.blueprints:
            app.register_blueprint(_error_bp)

    def test_404_returns_json(self, client):
        resp = client.get("/api/v1/this-route-does-not-exist")
        assert resp.status_code == 404
        data = resp.get_json()
        assert data["status"] == "error"
        assert "code" in data
        assert "message" in data

    def test_app_error_handler_project_not_found(self, client):
        resp = client.get("/test/project-not-found")
        assert resp.status_code == 404
        data = resp.get_json()
        assert data["status"] == "error"
        assert data["code"] == "PROJECT_NOT_FOUND"
        assert "99" in data["message"]

    def test_app_error_handler_validation_error(self, client):
        resp = client.get("/test/validation-error")
        assert resp.status_code == 422
        data = resp.get_json()
        assert data["code"] == "VALIDATION_ERROR"

    def test_app_error_handler_adapter_error(self, client):
        resp = client.get("/test/adapter-error")
        assert resp.status_code == 502
        data = resp.get_json()
        assert data["code"] == "ADAPTER_ERROR"

    def test_generic_exception_returns_500(self, client):
        resp = client.get("/test/unhandled")
        assert resp.status_code == 500
        data = resp.get_json()
        assert data["status"] == "error"
        assert data["code"] == "INTERNAL_ERROR"


# ---------------------------------------------------------------------------
# Utility layer smoke tests
# ---------------------------------------------------------------------------

class TestUtils:

    def test_utcnow_is_aware(self):
        from utils import utcnow
        dt = utcnow()
        assert dt.tzinfo is not None

    def test_to_iso_roundtrip(self):
        from utils import utcnow, to_iso, parse_iso
        now = utcnow()
        assert parse_iso(to_iso(now)).isoformat() == now.isoformat()

    def test_days_between(self):
        from utils import utcnow, add_days, days_between
        now = utcnow()
        future = add_days(now, 5)
        assert days_between(now, future) == 5

    def test_is_past_future(self):
        from utils import utcnow, add_days, is_past, is_future
        now = utcnow()
        assert is_future(add_days(now, 1))
        assert is_past(add_days(now, -1))

    def test_to_json_datetime(self):
        from utils import utcnow, to_json, from_json
        now = utcnow()
        serialized = to_json({"ts": now})
        parsed = from_json(serialized)
        assert "ts" in parsed

    def test_safe_get_nested(self):
        from utils import safe_get
        data = {"a": {"b": {"c": 42}}}
        assert safe_get(data, "a", "b", "c") == 42
        assert safe_get(data, "a", "x", default="missing") == "missing"

    def test_file_exists_false(self):
        from utils import file_exists
        assert not file_exists("/nonexistent/path/file.txt")

    def test_ensure_directory(self, tmp_path):
        from utils import ensure_directory
        new_dir = tmp_path / "sub" / "dir"
        result = ensure_directory(new_dir)
        assert result.exists()

    def test_get_file_extension(self):
        from utils import get_file_extension
        assert get_file_extension("report.PDF") == ".pdf"
        assert get_file_extension("data.json") == ".json"
