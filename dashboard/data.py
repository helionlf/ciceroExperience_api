from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Dict, Optional, Tuple

from django.utils import timezone


@dataclass(frozen=True)
class DateRange:
    start: date
    end: date
    label: str
    days: int
    active_key: str
    is_custom: bool

    @property
    def display(self) -> Dict[str, str]:
        return {
            "start": _format_human_date(self.start),
            "end": _format_human_date(self.end),
            "days": f"{self.days} dia{'s' if self.days != 1 else ''}",
        }


FILTER_OPTIONS: Tuple[Tuple[str, str], ...] = (
    ("today", "Hoje"),
    ("yesterday", "Ontem"),
    ("7d", "7 dias"),
    ("30d", "30 dias"),
)


def resolve_date_range(range_key: Optional[str], since: Optional[str], until: Optional[str]) -> DateRange:
    today = timezone.localdate()
    custom_range = _parse_custom_range(since, until)

    if custom_range:
        start, end = custom_range
        label = f"{_format_human_date(start)} – {_format_human_date(end)}"
        days = (end - start).days + 1
        return DateRange(start=start, end=end, label=label, days=days, active_key="custom", is_custom=True)

    start, end, label, resolved_key = _resolve_preset_range(range_key, today)
    days = (end - start).days + 1
    return DateRange(start=start, end=end, label=label, days=days, active_key=resolved_key, is_custom=False)


def _resolve_preset_range(range_key: Optional[str], today: date) -> Tuple[date, date, str, str]:
    if range_key == "yesterday":
        day = today - timedelta(days=1)
        return day, day, "Ontem", "yesterday"
    if range_key == "7d":
        start = today - timedelta(days=6)
        return start, today, "7 dias", "7d"
    if range_key == "30d":
        start = today - timedelta(days=29)
        return start, today, "30 dias", "30d"

    return today, today, "Hoje", "today"

def _parse_custom_range(since: Optional[str], until: Optional[str]) -> Optional[Tuple[date, date]]:
    """Parse dates in YYYY-MM-DD format"""
    if not since or not until:
        return None
    
    try:
        start = datetime.strptime(since, "%Y-%m-%d").date()
        end = datetime.strptime(until, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None
    
    if start > end:
        return None
    
    return start, end

def _parse_unix_timestamp(raw_value: Optional[str]) -> Optional[date]:
    if raw_value is None:
        return None

    try:
        numeric = int(raw_value)
    except (TypeError, ValueError):
        return None

    seconds = numeric / 1000 if numeric > 1_000_000_000_000 else numeric

    try:
        dt = datetime.fromtimestamp(seconds, tz=timezone.get_current_timezone())
    except (OSError, OverflowError, ValueError):
        return None

    return dt.date()


def _format_human_date(value: date) -> str:
    month_names = [
        "jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez",
    ]
    month = month_names[value.month - 1]
    return f"{value.day:02d} de {month}"
