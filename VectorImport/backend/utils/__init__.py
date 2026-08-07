"""
utils/__init__.py
-----------------
Public surface of the utils package.

    from utils import get_logger, setup_logging
    from utils import utcnow, to_iso
    from utils import to_json, from_json, safe_get
    from utils import file_exists, ensure_directory
"""

from utils.logger import get_logger, setup_logging
from utils.date_utils import (
    utcnow,
    local_now,
    to_iso,
    to_display,
    parse_iso,
    parse_date_string,
    add_days,
    add_hours,
    days_between,
    is_past,
    is_future,
)
from utils.json_utils import (
    AppJSONEncoder,
    to_json,
    from_json,
    load_json_file,
    save_json_file,
    safe_get,
)
from utils.file_utils import (
    file_exists,
    ensure_directory,
    get_file_extension,
    get_file_size_bytes,
)

__all__ = [
    # Logging
    "get_logger", "setup_logging",
    # Dates
    "utcnow", "local_now", "to_iso", "to_display",
    "parse_iso", "parse_date_string",
    "add_days", "add_hours", "days_between", "is_past", "is_future",
    # JSON
    "AppJSONEncoder", "to_json", "from_json",
    "load_json_file", "save_json_file", "safe_get",
    # Files
    "file_exists", "ensure_directory",
    "get_file_extension", "get_file_size_bytes",
]
