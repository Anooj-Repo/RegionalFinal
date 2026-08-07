"""
database/seed.py
----------------
Seeds the projects table with id, project_id, and name only.
All other project data is loaded on-demand from JSON via DataSourceRegistry.
"""

from __future__ import annotations

from database.models import Project
from extensions import db
from adapters.registry_config import PROJECT_REGISTRY
from services.data_source_registry import get_registry
from utils.logger import get_logger

_log = get_logger("database.seed")


def seed_database() -> None:
    """
    Seed the projects table with id, project_id, and name.
    Idempotent — skips if already seeded.
    """
    if Project.query.count() > 0:
        _log.info("Database already seeded (%d projects present).", Project.query.count())
        return

    _log.info("Seeding projects table from DataSourceRegistry...")
    registry = get_registry()

    for pid in sorted(PROJECT_REGISTRY.keys()):
        try:
            snapshot = registry.load_project(pid)
            p = snapshot.project

            db_project = Project(
                id=pid,
                project_id=p.project_id,
                name=p.name,
            )
            db.session.add(db_project)
            db.session.commit()
            _log.info("Seeded project pid=%d '%s' into database.", pid, p.name)
        except Exception as exc:
            db.session.rollback()
            _log.error("Failed to seed project pid=%d: %s", pid, exc)
            raise
