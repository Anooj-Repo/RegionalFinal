"""
utils/logger.py
---------------
Centralized logging factory for the entire project.

Every module should obtain its logger via:

    from utils.logger import get_logger
    logger = get_logger(__name__)

Features:
    ✔ Console handler  — colored, human-readable output
    ✔ File handler     — rotating daily log files in logs/
    ✔ Timestamp        — ISO-8601 with milliseconds
    ✔ Module name      — sourced from __name__ passed by each caller
    ✔ Log level        — read from LOG_LEVEL env-var / app config
    ✔ Single setup     — root logger configured once, never duplicated
"""

import logging
import os
import sys
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path


# ---------------------------------------------------------------------------
# ANSI colour codes (console only — stripped automatically by the formatter
# when the stream is not a TTY, e.g. when output is piped to a file)
# ---------------------------------------------------------------------------

_COLOURS: dict[str, str] = {
    "DEBUG":    "\033[36m",   # Cyan
    "INFO":     "\033[32m",   # Green
    "WARNING":  "\033[33m",   # Yellow
    "ERROR":    "\033[31m",   # Red
    "CRITICAL": "\033[35m",   # Magenta
}
_RESET = "\033[0m"


class _ColourFormatter(logging.Formatter):
    """Formatter that adds ANSI colour to the levelname when writing to a TTY."""

    def format(self, record: logging.LogRecord) -> str:
        if sys.stderr.isatty():
            colour = _COLOURS.get(record.levelname, "")
            record.levelname = f"{colour}{record.levelname:<8}{_RESET}"
        else:
            record.levelname = f"{record.levelname:<8}"
        return super().format(record)


# ---------------------------------------------------------------------------
# Internal state — the root application logger is initialised only once
# ---------------------------------------------------------------------------

_ROOT_LOGGER_NAME = "app"
_initialised = False


def _get_log_dir() -> Path:
    """Resolve the logs directory (relative to this file's package root)."""
    # utils/logger.py → backend/logs/
    return Path(__file__).resolve().parent.parent / "logs"


def setup_logging(level: str | None = None, log_dir: str | None = None) -> None:
    """
    Configure the root 'app' logger with a console handler and a
    daily-rotating file handler.

    Call this ONCE inside create_app() after loading config.

    Args:
        level:   Override log level string (e.g. "DEBUG", "INFO").
                 Falls back to LOG_LEVEL env-var, then "INFO".
        log_dir: Override log directory path.
                 Falls back to logs/ next to the backend root.
    """
    global _initialised
    if _initialised:
        return
    _initialised = True

    # ── Resolve level ────────────────────────────────────────────────────────
    resolved_level_str = (level or os.getenv("LOG_LEVEL", "INFO")).upper()
    resolved_level = getattr(logging, resolved_level_str, logging.INFO)

    # ── Resolve log directory ────────────────────────────────────────────────
    log_path = Path(log_dir) if log_dir else _get_log_dir()
    log_path.mkdir(parents=True, exist_ok=True)

    # ── Formatters ──────────────────────────────────────────────────────────
    _TIMESTAMP_FMT = "%Y-%m-%d %H:%M:%S"

    console_fmt = _ColourFormatter(
        fmt="[%(asctime)s.%(msecs)03d] %(levelname)s %(name)s — %(message)s",
        datefmt=_TIMESTAMP_FMT,
    )

    file_fmt = logging.Formatter(
        fmt="[%(asctime)s.%(msecs)03d] %(levelname)-8s %(name)s | %(filename)s:%(lineno)d — %(message)s",
        datefmt=_TIMESTAMP_FMT,
    )

    # ── Console handler (stderr) ─────────────────────────────────────────────
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setFormatter(console_fmt)
    console_handler.setLevel(resolved_level)

    # ── File handler (daily rotation, keep 30 days) ──────────────────────────
    file_handler = TimedRotatingFileHandler(
        filename=log_path / "app.log",
        when="midnight",       # rotate at midnight
        interval=1,            # every day
        backupCount=30,        # keep 30 days of logs
        encoding="utf-8",
        utc=False,
    )
    file_handler.setFormatter(file_fmt)
    file_handler.setLevel(resolved_level)
    file_handler.suffix = "%Y-%m-%d"  # app.log.2026-08-07

    # ── Root 'app' logger ────────────────────────────────────────────────────
    root = logging.getLogger(_ROOT_LOGGER_NAME)
    root.setLevel(resolved_level)
    root.addHandler(console_handler)
    root.addHandler(file_handler)
    root.propagate = False   # don't bubble up to the Python root logger

    root.info(
        "Logging initialised | level=%s | log_dir=%s",
        resolved_level_str,
        log_path,
    )


def get_logger(name: str) -> logging.Logger:
    """
    Return a child logger namespaced under the root 'app' logger.

    Args:
        name: Typically pass __name__ from the calling module.

    Returns:
        A Logger whose output is handled by the configured root logger.

    Example:
        from utils.logger import get_logger
        logger = get_logger(__name__)
        logger.info("Hello from %s", __name__)
    """
    # If setup_logging() hasn't been called yet (e.g. during testing),
    # fall back to a sensible default so modules don't silently discard logs.
    if not _initialised:
        setup_logging()

    return logging.getLogger(f"{_ROOT_LOGGER_NAME}.{name}")
