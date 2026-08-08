"""
utils/json_utils.py
-------------------
JSON serialization helpers — placeholders only.

Implementations will grow as the API and workflow layers are built.
"""

from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path
from typing import Any

from utils.logger import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Custom encoder
# ---------------------------------------------------------------------------

class AppJSONEncoder(json.JSONEncoder):
    """
    Extended JSON encoder that handles types the stdlib cannot:
        - datetime / date  → ISO-8601 string
        - Path             → POSIX string
        - set              → list (sorted for determinism)
    """

    def default(self, obj: Any) -> Any:
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, date):
            return obj.isoformat()
        if isinstance(obj, Path):
            return obj.as_posix()
        if isinstance(obj, set):
            return sorted(obj)
        return super().default(obj)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def to_json(obj: Any, *, indent: int | None = None) -> str:
    """
    Serialize an object to a JSON string using AppJSONEncoder.

    Args:
        obj:    Any JSON-serializable object.
        indent: Pretty-print indent width. None = compact.

    Returns:
        JSON string.
    """
    return json.dumps(obj, cls=AppJSONEncoder, ensure_ascii=False, indent=indent)


def from_json(text: str) -> Any:
    """
    Deserialize a JSON string.

    Args:
        text: Raw JSON string.

    Returns:
        Parsed Python object.

    Raises:
        json.JSONDecodeError: If text is not valid JSON.
    """
    return json.loads(text)


def load_json_file(path: str | Path) -> Any:
    """
    Read and parse a JSON file.

    Args:
        path: Path to the .json file.

    Returns:
        Parsed object.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    # TODO: Add schema validation (jsonschema) when needed
    p = Path(path)
    logger.debug("Loading JSON file: %s", p)
    with p.open(encoding="utf-8") as fh:
        return json.load(fh)


def save_json_file(path: str | Path, obj: Any, *, indent: int = 2) -> None:
    """
    Serialize an object and write it to a JSON file.

    Args:
        path:   Destination file path (.json).
        obj:    Object to serialize.
        indent: Pretty-print indent width.
    """
    # TODO: Add atomic write
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    logger.debug("Saving JSON file: %s", p)
    with p.open("w", encoding="utf-8") as fh:
        json.dump(obj, fh, cls=AppJSONEncoder, ensure_ascii=False, indent=indent)


def safe_get(data: dict, *keys: str, default: Any = None) -> Any:
    """
    Safely traverse a nested dict with dot-path keys.

    Args:
        data:    Source dictionary.
        *keys:   Key sequence to traverse.
        default: Value returned if any key is missing.

    Example:
        safe_get(resp, "data", "project", "id", default=0)
    """
    current = data
    for key in keys:
        if not isinstance(current, dict):
            return default
        current = current.get(key, default)
    return current
