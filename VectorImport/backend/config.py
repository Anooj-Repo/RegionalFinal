"""
config.py
---------
Environment-based configuration.

All values are read from environment variables (via .env).
No hardcoded paths or secrets anywhere in this file.

Usage inside create_app():
    from config import config_map
    app.config.from_object(config_map[env])
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from the directory that contains this file
_BASE_DIR = Path(__file__).resolve().parent
load_dotenv(_BASE_DIR / ".env")


def _require(key: str) -> str:
    """Read a required env-var; raise clearly if it is missing."""
    value = os.getenv(key)
    if not value:
        raise EnvironmentError(
            f"Required environment variable '{key}' is not set. "
            f"Check your .env file."
        )
    return value


def _path(key: str, default: str) -> str:
    """
    Read a path from env-var and make it absolute relative to BASE_DIR.
    Accepts absolute paths as-is.
    """
    raw = os.getenv(key, default)
    p = Path(raw)
    if not p.is_absolute():
        p = _BASE_DIR / p
    return str(p)


# ---------------------------------------------------------------------------
# Base Configuration
# ---------------------------------------------------------------------------

class BaseConfig:
    """Defaults shared across all environments."""

    # ── Identity ────────────────────────────────────────────────────────────
    APP_NAME: str       = os.getenv("APP_NAME", "ai-hackathon")
    ENVIRONMENT: str    = os.getenv("ENVIRONMENT", "development")
    APP_VERSION: str    = os.getenv("APP_VERSION", "1.0.0")
    SERVICE_NAME: str   = os.getenv("SERVICE_NAME", "Program Management AI Assistant")

    # ── Flask core ───────────────────────────────────────────────────────────
    SECRET_KEY: str     = os.getenv("SECRET_KEY", "")
    DEBUG: bool         = False
    TESTING: bool       = False

    # ── Database ─────────────────────────────────────────────────────────────
    DATABASE_URL: str               = os.getenv("DATABASE_URL", "")
    SQLALCHEMY_DATABASE_URI: str    = DATABASE_URL          # Flask-SQLAlchemy key
    SQLALCHEMY_TRACK_MODIFICATIONS  = False

    # ── Logging ──────────────────────────────────────────────────────────────
    LOG_LEVEL: str  = os.getenv("LOG_LEVEL", "INFO")
    LOG_DIR: str    = str(_BASE_DIR / "logs")

    # ── Embeddings ───────────────────────────────────────────────────────────
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

    # ── LLM (TCS GenAI Lab Integration Ready) ────────────────────────────────
    LLM_PROVIDER: str   = os.getenv("LLM_PROVIDER", "openai")
    LLM_API_KEY: str    = os.getenv("LLM_API_KEY", "")
    LLM_BASE_URL: str   = os.getenv("LLM_BASE_URL", "https://genailab.tcs.in/v1")
    LLM_MODEL: str      = os.getenv("LLM_MODEL", "gpt-4o-mini")

    # ── Vector Store ─────────────────────────────────────────────────────────
    VECTOR_DB_PATH: str = _path("VECTOR_DB_PATH", "data/vector_store")

    # ── Dataset ──────────────────────────────────────────────────────────────
    DATASET_PATH: str   = _path("DATASET_PATH", "data/dataset")

    # ── API ──────────────────────────────────────────────────────────────────
    API_PREFIX: str = "/api/v1"


# ---------------------------------------------------------------------------
# Environment-Specific Overrides
# ---------------------------------------------------------------------------

class DevelopmentConfig(BaseConfig):
    """Local development — verbose logging, SQLite."""
    DEBUG       = True
    LOG_LEVEL   = os.getenv("LOG_LEVEL", "DEBUG")


class TestingConfig(BaseConfig):
    """CI / unit tests — in-memory DB, minimal noise."""
    TESTING                 = True
    DEBUG                   = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    DATABASE_URL            = "sqlite:///:memory:"
    LOG_LEVEL               = "WARNING"


class ProductionConfig(BaseConfig):
    """
    Production — enforce required secrets at startup.

    _require() is called lazily inside validate() so the module can be
    imported without side-effects when variables are not yet set
    (e.g. during local development or test collection).
    Call ProductionConfig.validate() inside create_app() before use.
    """
    DEBUG       = False
    LOG_LEVEL   = os.getenv("LOG_LEVEL", "WARNING")

    # Read from env — empty string is fine here; validate() will catch blanks.
    SECRET_KEY              = os.getenv("SECRET_KEY", "")
    DATABASE_URL            = os.getenv("DATABASE_URL", "")
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    LLM_API_KEY             = os.getenv("LLM_API_KEY", "")

    @classmethod
    def validate(cls) -> None:
        """Fail fast if any required production variable is missing."""
        for key in ("SECRET_KEY", "DATABASE_URL", "LLM_API_KEY"):
            _require(key)


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

config_map: dict = {
    "development": DevelopmentConfig,
    "testing":     TestingConfig,
    "production":  ProductionConfig,
    "default":     DevelopmentConfig,
}

Config = BaseConfig


def get_config() -> type[BaseConfig]:
    """Return the active configuration class based on ENVIRONMENT env var."""
    env = os.getenv("ENVIRONMENT", "development").lower()
    return config_map.get(env, DevelopmentConfig)
