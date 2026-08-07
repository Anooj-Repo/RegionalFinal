"""
api/routes/__init__.py
----------------------
API Routes Package exporting project_bp and analysis_bp.
"""

from api.routes.project_routes import project_bp
from api.routes.analysis_routes import analysis_bp

__all__ = ["project_bp", "analysis_bp"]
