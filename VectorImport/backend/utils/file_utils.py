"""
utils/file_utils.py
-------------------
File system helpers — placeholders only.

Implementations will be added when file ingestion / RAG is built.
"""

from __future__ import annotations

import os
from pathlib import Path

from utils.logger import get_logger

logger = get_logger(__name__)


def read_text_file(path: str | Path) -> str:
    """
    Read a UTF-8 text file and return its contents as a string.

    Args:
        path: Absolute or relative path to the file.

    Returns:
        File content as a string.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    # TODO: Add encoding detection (chardet) and error handling
    raise NotImplementedError("read_text_file is not implemented yet.")


def write_text_file(path: str | Path, content: str) -> None:
    """
    Write a string to a UTF-8 text file, creating parent dirs if needed.

    Args:
        path:    Destination file path.
        content: Text to write.
    """
    # TODO: Implement atomic write (write to .tmp then rename)
    raise NotImplementedError("write_text_file is not implemented yet.")


def list_files(directory: str | Path, extension: str = "") -> list[Path]:
    """
    List all files in a directory, optionally filtered by extension.

    Args:
        directory: Directory to scan.
        extension: File extension filter, e.g. ".pdf". Empty = all files.

    Returns:
        Sorted list of matching Path objects.
    """
    # TODO: Implement recursive listing with glob
    raise NotImplementedError("list_files is not implemented yet.")


def file_exists(path: str | Path) -> bool:
    """Return True if the path points to an existing file."""
    return Path(path).is_file()


def ensure_directory(path: str | Path) -> Path:
    """
    Create a directory (and any parents) if it does not already exist.

    Returns:
        The resolved Path object.
    """
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    logger.debug("Directory ensured: %s", p)
    return p


def get_file_extension(path: str | Path) -> str:
    """Return the lowercase file extension including the dot, e.g. '.pdf'."""
    return Path(path).suffix.lower()


def get_file_size_bytes(path: str | Path) -> int:
    """Return the size of a file in bytes."""
    return os.path.getsize(path)
