"""
PlanWise AI - Intent Parser
Deterministic rule-based intent detection and entity extraction.
This is the primary fallback when no LLM is configured.
"""
import re
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple, List
from app.services.date_service import parse_natural_date, get_today


# ─── Intent Categories ────────────────────────────────────────────────────────

INTENTS = {
    "list_tasks": [
        r"\b(show|list|display|get|find|tell me about)\b.*(tasks?|assignments?|todos?|reminders?|schedule)",
        r"\bwhat (do i|should i|have i)\b.*(today|this week|tomorrow|overdue|to do|do|pending|left)",
        r"\bwhat (is|'s) (on|in) (my\s+)?schedule\b",
        r"\bwhat do i have to do\b",
        r"\bmy (tasks?|todos?|list|assignments?)\b",
    ],

    "prioritize": [
        r"\b(what|which).*(should i|do i|can i|to)\b.*(work on|focus|start|do) (first|next)",
        r"\b(prioritize|priorities|most important|urgent|top priority)\b",
        r"\bwhat should i (do|work on|focus on) (first|next|now|today)\b",
    ],
    "generate_schedule": [
        r"\b(plan|schedule|create|generate|make|build)\b.*(my day|schedule|timeline|plan)",
        r"\bplan (my|the) day\b",
        r"\bschedule (for|my)\b",
        r"\borganize my (day|tasks|time)\b",
    ],
    "complete_task": [
        r"\b(mark|set|complete|finish|done|check off)\b.*(as |)(complete|done|finished|completed)",
        r"\bi('ve| have| just| already| did) (finished|completed|done)\b",
    ],
    "update_task": [
        r"\b(update|change|edit|modify|move|reschedule|extend|push)\b.*(task|assignment|deadline|due date|priority)",
        r"\b(change|update|set)\b.*(deadline|due date|priority|title|name)\b",
    ],
    "delete_task": [
        r"\b(delete|remove|cancel|drop|get rid of)\b.*(task|assignment|reminder|meeting)",
    ],
    "create_task": [
        r"\b(add|create|new|make|set up|schedule)\b.*(task|assignment|reminder|todo|meeting|exam|project|homework)",
        r"^(?!.*what\b).*\b(i need to|i have to|remind me to|don'?t forget to)\b",
        r"\b(add|create)\b.*(for|by|due|before)\b",
    ],

    "available_time": [
        r"\bi have (\d+|one|two|three|four|five|six|an?)\s*(hour|hr|minute|min)",
        r"\b(\d+|one|two|three|four|five|six)\s*(hours?|hrs?|minutes?|mins?) (free|available|spare|left)",
        r"\bwhat can i (finish|complete|do) in\b",
    ],
    "overdue_tasks": [
        r"\b(overdue|late|past due|missed|behind)\b",
        r"\bwhat('?s| is| are) (overdue|late|behind)\b",
    ],
    "help": [
        r"^(help|what can you do|commands|how|usage)\b",
        r"\b(how do i|how can i|how to)\b",
        r"^hi$|^hello$|^hey$|^start$",
    ],
}


def detect_intent(message: str) -> str:
    """Detect the primary intent of a message."""
    msg_lower = message.lower().strip()

    for intent, patterns in INTENTS.items():
        for pattern in patterns:
            if re.search(pattern, msg_lower):
                return intent

    return "general"


def extract_task_name(message: str) -> Optional[str]:
    """Extract a task name or keyword from a message."""
    # Patterns like: "mark X as done", "delete X", "complete X"
    patterns = [
        r'(?:mark|complete|finish|delete|remove|cancel|update|change|edit)\s+(?:my\s+)?["\']?([^"\']+?)["\']?\s+(?:as|task|to)',
        r'(?:mark|complete|finish|delete|remove|cancel)\s+["\']([^"\']+)["\']',
        r'"([^"]+)"',
        r"'([^']+)'",
    ]
    for pattern in patterns:
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None


def extract_priority(message: str) -> Optional[str]:
    """Extract priority from message."""
    msg_lower = message.lower()
    if "urgent" in msg_lower or "critical" in msg_lower or "asap" in msg_lower:
        return "urgent"
    if "high priority" in msg_lower or "high" in msg_lower:
        return "high"
    if "medium priority" in msg_lower or "medium" in msg_lower:
        return "medium"
    if "low priority" in msg_lower or "low" in msg_lower:
        return "low"
    return None


def extract_duration(message: str) -> Optional[int]:
    """Extract estimated duration in minutes from message."""
    patterns = [
        (r"(\d+)\s*hours?\s*(?:and\s*)?(\d+)\s*(?:minutes?|mins?)", lambda m: int(m.group(1)) * 60 + int(m.group(2))),
        (r"(\d+\.?\d*)\s*hours?", lambda m: int(float(m.group(1)) * 60)),
        (r"(\d+)\s*(?:minutes?|mins?)", lambda m: int(m.group(1))),
        (r"half\s*(?:an?\s*)?hour", lambda m: 30),
        (r"(?:an?\s*)?hour\s*(?:and\s*a?\s*half)?", lambda m: 90),
    ]
    for pattern, handler in patterns:
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            try:
                return handler(match)
            except Exception:
                pass
    return None


def extract_date(message: str, timezone: str = "Asia/Kolkata") -> Tuple[Optional[str], Optional[str]]:
    """
    Extract a date from a message.
    Returns (date_str, ambiguity_note).
    """
    # Common date phrase patterns
    date_phrases = [
        r"(?:due|by|before|on|for|deadline)\s+(today|tomorrow|monday|tuesday|wednesday|thursday|friday|saturday|sunday|next \w+|this \w+|in \d+ days?)",
        r"(today|tomorrow|monday|tuesday|wednesday|thursday|friday|saturday|sunday|next \w+|this \w+|in \d+ days?|day after tomorrow)",
        r"(\d{4}-\d{2}-\d{2})",
        r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*\s+\d{1,2}",
    ]

    for pattern in date_phrases:
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            date_text = match.group(1).strip()
            date_str, note = parse_natural_date(date_text, timezone)
            if date_str:
                return date_str, note

    return None, None


def extract_time_window(message: str) -> Tuple[Optional[str], Optional[str]]:
    """Extract start and end times from a scheduling request."""
    # "from 9 AM to 5 PM" or "9:00 to 17:00"
    pattern = r"(?:from\s+)?(\d{1,2}(?::\d{2})?\s*(?:am|pm)?)\s+(?:to|until|till)\s+(\d{1,2}(?::\d{2})?\s*(?:am|pm)?)"
    match = re.search(pattern, message, re.IGNORECASE)
    if match:
        start = _normalize_time(match.group(1))
        end = _normalize_time(match.group(2))
        return start, end
    return None, None


def _normalize_time(time_str: str) -> str:
    """Normalize a time string to HH:MM 24-hour format."""
    time_str = time_str.strip()
    is_pm = "pm" in time_str.lower()
    is_am = "am" in time_str.lower()
    time_str = re.sub(r"[apm]+", "", time_str, flags=re.IGNORECASE).strip()

    if ":" in time_str:
        parts = time_str.split(":")
        h, m = int(parts[0]), int(parts[1])
    else:
        h = int(time_str)
        m = 0

    if is_pm and h != 12:
        h += 12
    elif is_am and h == 12:
        h = 0

    return f"{h:02d}:{m:02d}"


def extract_free_time(message: str) -> Optional[int]:
    """Extract available free time in minutes."""
    patterns = [
        (r"(\d+)\s*hours?\s*(?:and\s*)?(\d+)\s*(?:minutes?|mins?)\s+(?:free|available|spare|left)", lambda m: int(m.group(1)) * 60 + int(m.group(2))),
        (r"(\d+\.?\d*)\s*hours?\s+(?:free|available|spare|left)", lambda m: int(float(m.group(1)) * 60)),
        (r"(\d+)\s*(?:minutes?|mins?)\s+(?:free|available|spare|left)", lambda m: int(m.group(1))),
        (r"i have (\d+)\s*hours?", lambda m: int(m.group(1)) * 60),
        (r"i have (\d+)\s*(?:minutes?|mins?)", lambda m: int(m.group(1))),
    ]
    for pattern, handler in patterns:
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            try:
                return handler(match)
            except Exception:
                pass
    return None


def extract_task_title_from_create(message: str) -> Optional[str]:
    """Extract the task title from a create task message."""
    # Remove common prefixes
    prefixes = [
        r"^(?:please\s+)?(?:add|create|new|make|set up)\s+(?:a\s+|an\s+)?(?:new\s+)?(?:task\s+(?:to\s+|called|named|titled|:)?\s*)?",
        r"^(?:i need to|i have to|remind me to|don'?t forget to)\s+",
        r"^(?:add|create)\s+",
    ]

    msg = message.strip()
    for prefix in prefixes:
        msg = re.sub(prefix, "", msg, flags=re.IGNORECASE).strip()

    # Remove trailing date/priority info
    msg = re.sub(
        r"\s+(?:due|by|before|on|for|with|at|tomorrow|today|this|next).+$", "", msg,
        flags=re.IGNORECASE
    ).strip()
    msg = re.sub(
        r"\s+(?:high|low|medium|urgent)\s+priority\s*$", "", msg,
        flags=re.IGNORECASE
    ).strip()


    # Capitalize first letter
    if msg:
        return msg[0].upper() + msg[1:]
    return None
