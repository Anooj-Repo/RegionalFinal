"""
api/routes/project_routes.py
-----------------------------
Flask Blueprint for project metadata endpoints.
Zero business logic — delegates directly to ProjectController.
"""

from flask import Blueprint, Response
from api.controllers.project_controller import ProjectController

project_bp = Blueprint("project_bp", __name__)
_controller = ProjectController()


@project_bp.route("/projects", methods=["GET"])
def get_projects() -> Response:
    """GET /api/projects"""
    return _controller.get_projects()
