"""
factory.py
----------
Application Factory — the heart of the Flask app.

create_app()
    │
    ├─ 1. Load Config
    ├─ 2. Initialize Logging     (utils.logger.setup_logging)
    ├─ 3. Initialize Database    (SQLAlchemy + Migrate)
    ├─ 4. Initialize Extensions  (CORS, etc.)
    ├─ 5. Register Error Handlers
    ├─ 6. Register Blueprints
    └─ 7. Return Flask App
"""

import os

from flask import Flask

from config import config_map
from extensions import cors, db, migrate
from utils.logger import get_logger, setup_logging

logger = get_logger(__name__)


def create_app(env: str = "default") -> Flask:
    """
    Create and configure the Flask application.

    Args:
        env: One of 'development', 'testing', 'production', or 'default'.

    Returns:
        A fully configured Flask application instance.
    """
    app = Flask(__name__, instance_relative_config=False)

    # ------------------------------------------------------------------
    # 1. Load Config
    # ------------------------------------------------------------------
    cfg_class = config_map.get(env, config_map["default"])
    app.config.from_object(cfg_class)

    # In production, fail fast if required env-vars are missing.
    if env == "production" and hasattr(cfg_class, "validate"):
        cfg_class.validate()

    # ------------------------------------------------------------------
    # 2. Initialize Logging
    # ------------------------------------------------------------------
    setup_logging(
        level=app.config["LOG_LEVEL"],
        log_dir=app.config["LOG_DIR"],
    )
    logger.info("Starting app in '%s' environment.", env)

    # ------------------------------------------------------------------
    # 3. Initialize Database
    # ------------------------------------------------------------------
    _init_db(app)

    # ------------------------------------------------------------------
    # 4. Initialize Extensions
    # ------------------------------------------------------------------
    _init_extensions(app)

    # ------------------------------------------------------------------
    # 5. Register Error Handlers
    # ------------------------------------------------------------------
    _register_error_handlers(app)

    # ------------------------------------------------------------------
    # 6. Register Blueprints
    # ------------------------------------------------------------------
    _register_blueprints(app)

    # ------------------------------------------------------------------
    # 7. Return App
    # ------------------------------------------------------------------
    logger.info("Application factory complete — %s", app.config["APP_NAME"])
    return app


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _init_db(app: Flask) -> None:
    """Bind SQLAlchemy + Migrate, then create all tables."""
    from database.db import init_db

    db.init_app(app)
    migrate.init_app(app, db)
    init_db(app)


def _init_extensions(app: Flask) -> None:
    """Initialize remaining Flask extensions."""
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})


def _register_error_handlers(app: Flask) -> None:
    """Attach global exception handlers."""
    from exceptions.handlers import register_error_handlers
    register_error_handlers(app)


def _register_blueprints(app: Flask) -> None:
    """Register all route blueprints under API prefixes (/api/v1 and /api)."""
    from api.health import health_bp
    from api.routes import project_bp, analysis_bp

    prefix_v1 = app.config.get("API_PREFIX", "/api/v1")
    app.register_blueprint(health_bp, url_prefix=prefix_v1)
    app.register_blueprint(project_bp, url_prefix=prefix_v1)
    app.register_blueprint(analysis_bp, url_prefix=prefix_v1)

    if prefix_v1 != "/api":
        app.register_blueprint(health_bp, url_prefix="/api", name="health_bp_unversioned")
        app.register_blueprint(project_bp, url_prefix="/api", name="project_bp_unversioned")
        app.register_blueprint(analysis_bp, url_prefix="/api", name="analysis_bp_unversioned")
