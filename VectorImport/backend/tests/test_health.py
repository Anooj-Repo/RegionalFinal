"""
tests/test_health.py
--------------------
Tests for GET /health and GET /version endpoints.
"""

import pytest


# ---------------------------------------------------------------------------
# GET /health
# ---------------------------------------------------------------------------

class TestHealth:
    def test_returns_200(self, client):
        resp = client.get("/api/v1/health")
        assert resp.status_code == 200

    def test_status_is_healthy(self, client):
        data = client.get("/api/v1/health").get_json()
        assert data["status"] == "healthy"

    def test_required_fields_present(self, client):
        data = client.get("/api/v1/health").get_json()
        for field in ("status", "service", "version", "environment", "database"):
            assert field in data, f"Missing field: '{field}'"

    def test_service_name(self, client):
        data = client.get("/api/v1/health").get_json()
        assert data["service"] == "Program Management AI Assistant"

    def test_version_format(self, client):
        data = client.get("/api/v1/health").get_json()
        parts = data["version"].split(".")
        assert len(parts) == 3, "Version must be semver: MAJOR.MINOR.PATCH"

    def test_database_status_ok(self, client):
        data = client.get("/api/v1/health").get_json()
        assert data["database"]["status"] == "ok"

    def test_exact_example_shape(self, client):
        """Matches the spec example: status/service/version."""
        data = client.get("/api/v1/health").get_json()
        assert data == {
            "status":      "healthy",
            "service":     data["service"],     # accept any non-empty string
            "version":     data["version"],
            "environment": data["environment"],
            "database":    {"status": "ok"},
        }


# ---------------------------------------------------------------------------
# GET /version
# ---------------------------------------------------------------------------

class TestVersion:
    def test_returns_200(self, client):
        resp = client.get("/api/v1/version")
        assert resp.status_code == 200

    def test_status_is_success(self, client):
        data = client.get("/api/v1/version").get_json()
        assert data["status"] == "success"

    def test_required_fields_present(self, client):
        data = client.get("/api/v1/version").get_json()
        for field in ("status", "service", "version", "environment", "python_version"):
            assert field in data, f"Missing field: '{field}'"

    def test_python_version_format(self, client):
        data = client.get("/api/v1/version").get_json()
        parts = data["python_version"].split(".")
        assert len(parts) >= 2

    def test_service_name(self, client):
        data = client.get("/api/v1/version").get_json()
        assert data["service"] == "Program Management AI Assistant"

    def test_version_matches_health(self, client):
        """Both endpoints must report the same version string."""
        health_v  = client.get("/api/v1/health").get_json()["version"]
        version_v = client.get("/api/v1/version").get_json()["version"]
        assert health_v == version_v


# ---------------------------------------------------------------------------
# Pydantic base model unit tests
# ---------------------------------------------------------------------------

class TestBaseSchemas:
    def test_base_response_success(self):
        from schemas import BaseResponse
        r = BaseResponse(status="success", message="ok", data={"key": "value"})
        d = r.model_dump()
        assert d["status"] == "success"
        assert d["data"] == {"key": "value"}

    def test_base_response_error(self):
        from schemas import BaseResponse
        r = BaseResponse(status="error", errors=["Something went wrong"])
        assert r.errors == ["Something went wrong"]
        assert r.data is None

    def test_base_entity_requires_id(self):
        from schemas import BaseEntity
        import pytest
        with pytest.raises(Exception):
            BaseEntity()   # missing required `id`

    def test_base_entity_with_id(self):
        from schemas import BaseEntity
        e = BaseEntity(id=1)
        assert e.id == 1
        assert e.created_at is None

    def test_base_timestamp_model(self):
        from schemas import BaseTimestampModel
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        m = BaseTimestampModel(created_at=now, updated_at=now)
        assert m.created_at == now

    def test_base_entity_inherits_timestamps(self):
        from schemas import BaseEntity
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        e = BaseEntity(id=5, created_at=now)
        assert e.id == 5
        assert e.created_at == now

    def test_base_response_exclude_none(self):
        from schemas import BaseResponse
        r = BaseResponse(status="healthy")
        dumped = r.model_dump(exclude_none=True)
        # Only 'status' is set, others should be absent
        assert "data" not in dumped
        assert "errors" not in dumped
        assert "message" not in dumped
