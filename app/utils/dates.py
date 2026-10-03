from __future__ import annotations
import re
from datetime import datetime, timedelta, timezone


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def add_business_days(start: datetime, days: int) -> datetime:
    current = start
    added = 0
    while added < days:
        current += timedelta(days=1)
        if current.weekday() < 5:
            added += 1
    return current


def followup_due_at(timing: str | None, start: datetime | None = None) -> datetime | None:
    """Convert common model/demo timing phrases into an actual due timestamp.

    Unknown timing text deliberately returns None so the UI puts it in Needs Review
    instead of pretending a date was understood.
    """
    if not timing:
        return None
    start = start or utcnow()
    text = timing.strip().lower()
    if "today" in text:
        return start
    if "tomorrow" in text:
        return start + timedelta(days=1)
    match = re.search(r"(?:in\s+)?(\d+)\s+business\s+days?", text)
    if match:
        return add_business_days(start, int(match.group(1)))
    match = re.search(r"(?:in\s+)?(\d+)\s+days?", text)
    if match:
        return start + timedelta(days=int(match.group(1)))
    if "next week" in text or "1 week" in text or "one week" in text:
        return start + timedelta(days=7)
    return None
