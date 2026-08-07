"""
api/controllers/project_controller.py
--------------------------------------
ProjectController — Lists projects.

The DB (projects table) is the source of truth for id, project_id, and name.
All detail data (status, tasks, risks, etc.) is loaded on-demand from JSON
datasets via DataSourceRegistry.
"""

from __future__ import annotations

from typing import Any
from flask import jsonify, Response
from database.repositories import ProjectRepository
from services.data_source_registry import get_registry
from utils.logger import get_logger

_log = get_logger("api.controllers.project")


class ProjectController:

    def get_projects(self) -> Response:
        """
        GET /api/projects
        Returns all projects. id/project_id/name from DB; detail from JSON.
        """
        _log.info("[ProjectController] Fetching project list from database")

        try:
            projects = ProjectRepository.get_all()
        except Exception as exc:
            _log.exception("[ProjectController] Failed to read projects table: %s", exc)
            return jsonify({"error": "Failed to fetch projects", "detail": str(exc)}), 500

        if not projects:
            return jsonify([]), 200

        registry = get_registry()
        projects_list: list[dict[str, Any]] = []

        for p in sorted(projects, key=lambda x: x.id):
            # Base fields always come from DB
            entry: dict[str, Any] = {
                "id":         p.id,
                "project_id": p.project_id,
                "name":       p.name,
            }

            # Detail fields enriched from JSON dataset via DataSourceRegistry
            try:
                snapshot = registry.load_project(p.id)
                sp = snapshot.project
                tasks = snapshot.tasks
                entry.update({
                    "description":        sp.description,
                    "status":             sp.status.value,
                    "start_date":         sp.start_date.isoformat() if sp.start_date else None,
                    "end_date":           sp.end_date.isoformat() if sp.end_date else None,
                    "program_manager":    sp.program_manager,
                    "sponsor":            sp.sponsor,
                    "total_tasks":        len(tasks),
                    "blocked_tasks":      len(snapshot.blocked_tasks),
                    "open_risks":         len(snapshot.open_risks),
                    "total_stakeholders": len(snapshot.stakeholders),
                    "total_documents":    snapshot.total_documents,
                    "completion_pct":     round(
                        sum(t.completion for t in tasks) / len(tasks), 1
                    ) if tasks else 0.0,
                })
            except Exception as exc:
                _log.warning(
                    "[ProjectController] Could not enrich project id=%d from JSON registry: %s",
                    p.id, exc,
                )

            projects_list.append(entry)

        _log.info("[ProjectController] Returning %d projects", len(projects_list))
        return jsonify(projects_list), 200

        # Fallback to DataSourceRegistry
        registry = get_registry()
        projects_list = []
        for pid in sorted(PROJECT_REGISTRY.keys()):
            try:
                snapshot = registry.load_project(pid)
                projects_list.append({
                    "id": pid,
                    "project_id": snapshot.project.project_id,
                    "name": snapshot.project.name,
                    "description": snapshot.project.description,
                    "start_date": snapshot.project.start_date.isoformat() if snapshot.project.start_date else None,
                    "end_date": snapshot.project.end_date.isoformat() if snapshot.project.end_date else None,
                    "status": snapshot.project.status.value,
                    "program_manager": snapshot.project.program_manager,
                    "sponsor": snapshot.project.sponsor,
                    "total_tasks": len(snapshot.tasks),
                    "blocked_tasks": len(snapshot.blocked_tasks),
                    "open_risks": len(snapshot.open_risks),
                    "total_stakeholders": len(snapshot.stakeholders),
                    "total_documents": snapshot.total_documents,
                })
            except Exception as exc2:
                _log.error("[ProjectController] Failed to load project snapshot pid=%d: %s", pid, exc2)

        return jsonify(projects_list), 200
