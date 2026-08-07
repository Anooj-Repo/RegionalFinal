"""
tests/conftest.py
-----------------
Pytest configuration and shared fixtures.
"""

import pytest
from factory import create_app
from extensions import db as _db


@pytest.fixture(scope="session")
def app():
    """Create a testing Flask app for the full session."""
    application = create_app("testing")
    ctx = application.app_context()
    ctx.push()
    yield application
    ctx.pop()


@pytest.fixture(scope="session")
def db(app):
    """Create all tables once per session, drop after."""
    _db.create_all()
    yield _db
    _db.drop_all()


@pytest.fixture(scope="function")
def client(app):
    """A test client for HTTP-level tests."""
    return app.test_client()
