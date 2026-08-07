"""
database/db.py
--------------
Database initialization, seeding, and lifecycle helpers.

The SQLAlchemy instance (db) lives in extensions.py.
This module exposes:

    init_db(app)   — called by the factory; creates tables if absent and seeds data
    drop_db(app)   — for testing teardown only
    health_check() — confirms the DB is reachable (used by /health endpoint)
"""

import logging

from extensions import db

logger = logging.getLogger("app.database.db")


# ---------------------------------------------------------------------------
# Initialization & Seeding
# ---------------------------------------------------------------------------

def init_db(app) -> None:
    """
    Create all tables that do not yet exist in the database and seed records.

    Safe to call repeatedly — SQLAlchemy's create_all() is idempotent
    (it skips tables that are already present).

    Called automatically by factory._init_db().
    """
    with app.app_context():
        # Ensure all model classes are registered with the metadata
        _import_models()

        db.create_all()
        logger.info(
            "Database initialised — %d table(s) in metadata.",
            len(db.metadata.tables),
        )
        _log_table_names()

        # Seed data automatically for non-testing environments
        if not app.config.get("TESTING"):
            try:
                from database.seed import seed_database
                seed_database()
            except Exception as exc:
                logger.warning("Automatic database seeding failed: %s", exc)


def drop_db(app) -> None:
    """
    Drop ALL tables.

    ⚠️  For use in TESTING only — destroys all data permanently.
    """
    with app.app_context():
        _import_models()
        db.drop_all()
        logger.warning("All database tables dropped.")


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

def health_check() -> dict:
    """
    Execute a lightweight query to verify the database is reachable.

    Returns:
        dict with keys 'status' ("ok" | "error") and optionally 'detail'.
    """
    try:
        db.session.execute(db.text("SELECT 1"))
        return {"status": "ok"}
    except Exception as exc:  # noqa: BLE001
        logger.error("Database health check failed: %s", exc)
        return {"status": "error", "detail": str(exc)}


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _import_models() -> None:
    """
    Import all model modules so their classes are registered with
    SQLAlchemy's metadata before create_all() / drop_all() is called.
    """
    from database import models  # noqa: F401 — side-effect import


def _log_table_names() -> None:
    """Log the names of all managed tables at DEBUG level."""
    tables = sorted(db.metadata.tables.keys())
    logger.debug("Managed tables: %s", ", ".join(tables))
