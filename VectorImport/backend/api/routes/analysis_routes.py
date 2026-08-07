"""
api/routes/analysis_routes.py
------------------------------
Flask Blueprint for graph execution endpoints.
Zero business logic — delegates directly to AnalysisController.
"""

from flask import Blueprint, Response
from api.controllers.analysis_controller import AnalysisController

analysis_bp = Blueprint("analysis_bp", __name__)
_controller = AnalysisController()


@analysis_bp.route("/projects/<project_id>/knowledge", methods=["POST"])
def execute_knowledge(project_id: str) -> Response:
    """POST /api/projects/<project_id>/knowledge"""
    return _controller.execute_knowledge(project_id)


@analysis_bp.route("/projects/<project_id>/intelligence", methods=["POST"])
def execute_intelligence(project_id: str) -> Response:
    """POST /api/projects/<project_id>/intelligence"""
    return _controller.execute_intelligence(project_id)


@analysis_bp.route("/projects/<project_id>/analysis", methods=["POST"])
def execute_analysis(project_id: str) -> Response:
    """POST /api/projects/<project_id>/analysis"""
    return _controller.execute_analysis(project_id)


@analysis_bp.route("/projects/<project_id>/analyze", methods=["POST"])
def execute_full_analysis(project_id: str) -> Response:
    """POST /api/projects/<project_id>/analyze"""
    return _controller.execute_full_analysis(project_id)
