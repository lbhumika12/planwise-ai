"""
PlanWise AI - Date Service
Natural language date parsing and timezone handling.
Supports: today, tomorrow, this week, next week, day names, relative dates.
"""
from datetime import datetime, date, timedelta
from typing import Optional, Tuple
import re
import pytz
from dateutil import parser as dateutil_parser


def get_now(timezone: str = "Asia/Kolkata") -> datetime:
    """Get current datetime in specified timezone."""
    tz = pytz.timezone(timezone)
    return datetime.now(tz)


def get_today(timezone: str = "Asia/Kolkata") -> date:
    """Get today's date in specified timezone."""
    return get_now(timezone).date()


def parse_natural_date(
    text: str,
    timezone: str = "Asia/Kolkata",
    reference_date: Optional[date] = None,
) -> Tuple[Optional[str], Optional[str]]:
    """
    Parse a natural language date expression.
    Returns (date_str: YYYY-MM-DD, ambiguity_reason: str | None)
    If date cannot be parsed, returns (None, reason).
    """
    if not text or not text.strip():
        return None, "No date text provided"

    text = text.strip().lower()
    ref = reference_date or get_today(timezone)

    # Exact patterns
    patterns = [
        (r"^today$", lambda m: ref),
        (r"^tonight$", lambda m: ref),
        (r"^tomorrow$", lambda m: ref + timedelta(days=1)),
        (r"^day after tomorrow$", lambda m: ref + timedelta(days=2)),
        (r"^day after tom\b", lambda m: ref + timedelta(days=2)),
        (r"^yesterday$", lambda m: ref - timedelta(days=1)),
        (r"^this week$", lambda m: ref),  # start of period
        (r"^next week$", lambda m: ref + timedelta(weeks=1)),
        (r"^in (\d+) days?$", lambda m: ref + timedelta(days=int(m.group(1)))),
        (r"^in (\d+) weeks?$", lambda m: ref + timedelta(weeks=int(m.group(1)))),
        (r"^(\d+) days? from now$", lambda m: ref + timedelta(days=int(m.group(1)))),
        (r"^(\d+) days? later$", lambda m: ref + timedelta(days=int(m.group(1)))),
        (r"^end of week$", lambda m: _end_of_week(ref)),
        (r"^end of month$", lambda m: _end_of_month(ref)),
        (r"^this (monday|tuesday|wednesday|thursday|friday|saturday|sunday)$",
         lambda m: _this_weekday(ref, m.group(1))),
        (r"^next (monday|tuesday|wednesday|thursday|friday|saturday|sunday)$",
         lambda m: _next_weekday(ref, m.group(1))),
        (r"^(monday|tuesday|wednesday|thursday|friday|saturday|sunday)$",
         lambda m: _nearest_weekday(ref, m.group(1))),
    ]

    for pattern, handler in patterns:
        m = re.match(pattern, text)
        if m:
            try:
                result = handler(m)
                if isinstance(result, date):
                    return result.strftime("%Y-%m-%d"), None
                return result, None
            except Exception:
                pass

    # Try YYYY-MM-DD
    if re.match(r"^\d{4}-\d{2}-\d{2}$", text):
        try:
            datetime.strptime(text, "%Y-%m-%d")
            return text, None
        except ValueError:
            return None, f"Invalid date: {text}"

    # Try dateutil for more complex formats like "Jan 5", "5th January", "01/15"
    try:
        parsed = dateutil_parser.parse(text, default=datetime(ref.year, ref.month, ref.day))
        parsed_date = parsed.date()
        # If parsed date is in the past and no year was specified, bump to next year
        if parsed_date < ref and str(ref.year) not in text:
            parsed_date = parsed_date.replace(year=ref.year + 1)
        return parsed_date.strftime("%Y-%m-%d"), None
    except Exception:
        pass

    return None, f"Could not interpret date: '{text}'"


def _end_of_week(ref: date) -> date:
    """Return Sunday of the current week."""
    days_until_sunday = 6 - ref.weekday()
    return ref + timedelta(days=days_until_sunday)


def _end_of_month(ref: date) -> date:
    """Return last day of current month."""
    if ref.month == 12:
        return date(ref.year + 1, 1, 1) - timedelta(days=1)
    return date(ref.year, ref.month + 1, 1) - timedelta(days=1)


WEEKDAYS = {
    "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
    "friday": 4, "saturday": 5, "sunday": 6
}


def _this_weekday(ref: date, day_name: str) -> date:
    """Return the date of the named weekday in the current week (Monday=start)."""
    target_wd = WEEKDAYS[day_name]
    current_wd = ref.weekday()
    diff = target_wd - current_wd
    if diff < 0:
        diff += 7
    return ref + timedelta(days=diff)


def _next_weekday(ref: date, day_name: str) -> date:
    """Return the date of the named weekday in the NEXT week."""
    return _this_weekday(ref, day_name) + timedelta(weeks=1)


def _nearest_weekday(ref: date, day_name: str) -> date:
    """Return the nearest future occurrence of a weekday."""
    target_wd = WEEKDAYS[day_name]
    current_wd = ref.weekday()
    diff = target_wd - current_wd
    if diff <= 0:
        diff += 7  # Always move to next occurrence
    return ref + timedelta(days=diff)


def is_overdue(due_date_str: Optional[str], timezone: str = "Asia/Kolkata") -> bool:
    """Check if a date string (YYYY-MM-DD) is overdue."""
    if not due_date_str:
        return False
    try:
        due = datetime.strptime(due_date_str, "%Y-%m-%d").date()
        today = get_today(timezone)
        return due < today
    except Exception:
        return False


def format_relative_date(date_str: Optional[str], timezone: str = "Asia/Kolkata") -> str:
    """Format a date string as a human-readable relative expression."""
    if not date_str:
        return "No due date"
    try:
        due = datetime.strptime(date_str, "%Y-%m-%d").date()
        today = get_today(timezone)
        delta = (due - today).days

        if delta < 0:
            abs_days = abs(delta)
            return f"{abs_days} day{'s' if abs_days != 1 else ''} overdue"
        elif delta == 0:
            return "Due today"
        elif delta == 1:
            return "Due tomorrow"
        elif delta <= 7:
            return f"Due in {delta} days"
        else:
            return f"Due {due.strftime('%b %d')}"
    except Exception:
        return date_str
