"""
utils/date_utils.py
-------------------
Date and time helpers — placeholders only.

All functions work in UTC by default to avoid timezone surprises.
"""

from __future__ import annotations

from datetime import datetime, timezone, timedelta
from typing import Optional


# ---------------------------------------------------------------------------
# Now / current time
# ---------------------------------------------------------------------------

def utcnow() -> datetime:
    """Return the current UTC datetime (timezone-aware)."""
    return datetime.now(tz=timezone.utc)


def local_now() -> datetime:
    """Return the current local datetime (timezone-aware)."""
    return datetime.now().astimezone()


# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------

def to_iso(dt: datetime) -> str:
    """
    Format a datetime as an ISO-8601 string.

    Example:
        "2026-08-07T10:30:00+00:00"
    """
    return dt.isoformat()


def to_display(dt: datetime, fmt: str = "%d %b %Y, %H:%M") -> str:
    """
    Format a datetime for human display.

    Args:
        dt:  The datetime to format.
        fmt: strftime format string.

    Example:
        "07 Aug 2026, 10:30"
    """
    return dt.strftime(fmt)


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

def parse_iso(value: str) -> datetime:
    """
    Parse an ISO-8601 string to a timezone-aware datetime (UTC).

    Args:
        value: ISO-8601 string, e.g. "2026-08-07T10:30:00Z".

    Returns:
        UTC-aware datetime.

    Raises:
        ValueError: If the string cannot be parsed.
    """
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def parse_date_string(value: str, fmt: str = "%Y-%m-%d") -> datetime:
    """
    Parse a date string (no time component) to a UTC midnight datetime.

    Args:
        value: Date string, e.g. "2026-08-07".
        fmt:   strptime format.

    Returns:
        UTC-aware datetime at midnight.
    """
    return datetime.strptime(value, fmt).replace(tzinfo=timezone.utc)


# ---------------------------------------------------------------------------
# Arithmetic
# ---------------------------------------------------------------------------

def add_days(dt: datetime, days: int) -> datetime:
    """Return dt + N calendar days."""
    return dt + timedelta(days=days)


def add_hours(dt: datetime, hours: int) -> datetime:
    """Return dt + N hours."""
    return dt + timedelta(hours=hours)


def days_between(start: datetime, end: datetime) -> int:
    """
    Return the number of whole days between two datetimes.

    Always returns a non-negative integer (abs value).
    """
    return abs((end - start).days)


def is_past(dt: datetime) -> bool:
    """Return True if dt is strictly before the current UTC time."""
    return dt < utcnow()


def is_future(dt: datetime) -> bool:
    """Return True if dt is strictly after the current UTC time."""
    return dt > utcnow()


# ---------------------------------------------------------------------------
# Placeholders — to be implemented when scheduling / SLA logic is built
# ---------------------------------------------------------------------------

def business_days_between(start: datetime, end: datetime) -> int:
    """
    Return the number of business days (Mon–Fri) between two dates.

    TODO: Implement using a holiday calendar (e.g. `holidays` package).
    """
    raise NotImplementedError("business_days_between is not implemented yet.")


def next_business_day(dt: datetime) -> datetime:
    """
    Return the next business day after dt.

    TODO: Implement with holiday awareness.
    """
    raise NotImplementedError("next_business_day is not implemented yet.")
