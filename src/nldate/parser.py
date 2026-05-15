import calendar
import re
from datetime import date, timedelta

WEEKDAYS: dict[str, int] = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}

MONTH_MAP: dict[str, int] = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
    "jan": 1,
    "feb": 2,
    "mar": 3,
    "apr": 4,
    "jun": 6,
    "jul": 7,
    "aug": 8,
    "sep": 9,
    "sept": 9,
    "oct": 10,
    "nov": 11,
    "dec": 12,
}

ORD = r"(?:st|nd|rd|th)"
ORDINAL_RE = rf"(\d+){ORD}?"
NUM_RE = r"(\d+)"


def _next_weekday(today: date, target: int) -> date:
    days_ahead = target - today.weekday()
    if days_ahead < 0:
        days_ahead += 7
    elif days_ahead == 0:
        return today
    return today + timedelta(days=days_ahead)


def _prev_weekday(today: date, target: int) -> date:
    days_behind = today.weekday() - target
    if days_behind < 0:
        days_behind += 7
    elif days_behind == 0:
        return today
    return today - timedelta(days=days_behind)


def _this_weekday(today: date, target: int) -> date:
    if today.weekday() == target:
        return today
    return _next_weekday(today, target)


def _add_unit(base: date, unit: str, amount: int) -> date:
    if unit in ("day", "days"):
        return base + timedelta(days=amount)
    if unit in ("week", "weeks"):
        return base + timedelta(weeks=amount)
    if unit in ("month", "months"):
        total = base.year * 12 + base.month - 1 + amount
        y = total // 12
        m = total % 12 + 1
        last = calendar.monthrange(y, m)[1]
        return date(y, m, min(base.day, last))
    if unit in ("year", "years"):
        last = calendar.monthrange(base.year + amount, base.month)[1]
        return date(base.year + amount, base.month, min(base.day, last))
    return base


def _resolve_base(s: str, today: date) -> date | None:
    s = s.strip().lower()
    s = re.sub(r"^the\s+", "", s)
    if s in ("today", ""):
        return today
    if s == "tomorrow":
        return today + timedelta(days=1)
    if s == "yesterday":
        return today - timedelta(days=1)
    if s == "day after tomorrow":
        return today + timedelta(days=2)
    if s == "day before yesterday":
        return today - timedelta(days=2)
    if s == "now":
        return today
    return None


def _parse_absolute(s: str) -> date | None:
    s = s.strip()
    match = re.match(r"^(\d{4})[-/](\d{1,2})[-/](\d{1,2})$", s)
    if match:
        return date(int(match.group(1)), int(match.group(2)), int(match.group(3)))
    match = re.match(r"^(\d{1,2})[-/](\d{1,2})[-/](\d{4})$", s)
    if match:
        return date(int(match.group(3)), int(match.group(1)), int(match.group(2)))
    match = re.match(
        r"^([A-Za-z]+\.?)\s+" + ORDINAL_RE + r"\s*,?\s*(\d{4})$", s, re.IGNORECASE
    )
    if match and match.group(1).lower().rstrip(".") in MONTH_MAP:
        return date(
            int(match.group(3)),
            MONTH_MAP[match.group(1).lower().rstrip(".")],
            int(match.group(2)),
        )
    match = re.match(
        r"^([A-Za-z]+\.?)\s+" + r"(\d{1,2})" + r"\s*,?\s*(\d{4})$", s, re.IGNORECASE
    )
    if match and match.group(1).lower().rstrip(".") in MONTH_MAP:
        return date(
            int(match.group(3)),
            MONTH_MAP[match.group(1).lower().rstrip(".")],
            int(match.group(2)),
        )
    match = re.match(
        r"^" + ORDINAL_RE + r"\s+([A-Za-z]+\.?)\s*,?\s*(\d{4})$", s, re.IGNORECASE
    )
    if match and match.group(2).lower().rstrip(".") in MONTH_MAP:
        return date(
            int(match.group(3)),
            MONTH_MAP[match.group(2).lower().rstrip(".")],
            int(match.group(1)),
        )
    match = re.match(r"^(\d{1,2})\s+([A-Za-z]+\.?)\s*,?\s*(\d{4})$", s, re.IGNORECASE)
    if match and match.group(2).lower().rstrip(".") in MONTH_MAP:
        return date(
            int(match.group(3)),
            MONTH_MAP[match.group(2).lower().rstrip(".")],
            int(match.group(1)),
        )
    return None


def _parse_weekday(s: str, today: date) -> date | None:
    s = s.strip().lower()
    parts = s.split(None, 1)
    prefix = parts[0]
    rest = parts[1] if len(parts) > 1 else ""

    if rest in WEEKDAYS:
        wd = WEEKDAYS[rest]
        if prefix == "next":
            return _next_weekday(today, wd)
        if prefix == "last":
            return _prev_weekday(today, wd)
        if prefix == "this":
            return _this_weekday(today, wd)

    if s in WEEKDAYS:
        return _next_weekday(today, WEEKDAYS[s])

    return None


NUMBER_WORDS: dict[str, str] = {
    "one": "1",
    "two": "2",
    "three": "3",
    "four": "4",
    "five": "5",
    "six": "6",
    "seven": "7",
    "eight": "8",
    "nine": "9",
    "ten": "10",
}


def _replace_number_words(s: str) -> str:
    for word, digit in NUMBER_WORDS.items():
        s = re.sub(rf"\b{word}\b", digit, s)
    return s


def _parse(s: str, today: date) -> date | None:
    s = s.strip().lower()
    s = re.sub(r"^the\s+", "", s)
    s = re.sub(r"\ba\b", "1", s)
    s = re.sub(r"\ban\b", "1", s)
    s = _replace_number_words(s)

    if not s:
        return today
    if s == "today":
        return today
    if s == "tomorrow":
        return today + timedelta(days=1)
    if s == "yesterday":
        return today - timedelta(days=1)
    if s == "day after tomorrow":
        return today + timedelta(days=2)
    if s == "day before yesterday":
        return today - timedelta(days=2)
    if s == "next week":
        return today + timedelta(weeks=1)
    if s == "last week":
        return today - timedelta(weeks=1)

    if s == "next month":
        m = today.month + 1
        y = today.year
        if m > 12:
            m = 1
            y += 1
        last = calendar.monthrange(y, m)[1]
        return date(y, m, min(today.day, last))

    if s == "last month":
        m = today.month - 1
        y = today.year
        if m < 1:
            m = 12
            y -= 1
        last = calendar.monthrange(y, m)[1]
        return date(y, m, min(today.day, last))

    if s == "next year":
        last = calendar.monthrange(today.year + 1, today.month)[1]
        return date(today.year + 1, today.month, min(today.day, last))

    if s == "last year":
        last = calendar.monthrange(today.year - 1, today.month)[1]
        return date(today.year - 1, today.month, min(today.day, last))

    wk = _parse_weekday(s, today)
    if wk is not None:
        return wk

    match = re.match(
        r"(\d+)\s+(days?|weeks?|months?|years?)"
        r"(?:(?:\s+and\s+|,\s*)(\d+)\s+(days?|weeks?|months?|years?))?"
        r"\s+(before|after)\s+(.+)$",
        s,
    )
    if match:
        amount1 = int(match.group(1))
        unit1 = match.group(2).rstrip("s")
        relation = match.group(5)
        rest_str = match.group(6).strip()

        base = _resolve_base(rest_str, today)
        if base is None:
            base = _parse_absolute(rest_str)
        if base is None:
            wk_resolved = _parse_weekday(rest_str, today)
            if wk_resolved is not None:
                base = wk_resolved
        if base is None:
            return None

        result = _add_unit(base, unit1, amount1 if relation == "after" else -amount1)

        if match.group(3) is not None and match.group(4) is not None:
            amount2 = int(match.group(3))
            unit2 = match.group(4).rstrip("s")
            result = _add_unit(
                result, unit2, amount2 if relation == "after" else -amount2
            )

        return result

    match = re.match(
        r"(\d+)\s+(days?|weeks?|months?|years?)\s+"
        r"(before|after|from)\s+(.+)$",
        s,
    )
    if match:
        amount = int(match.group(1))
        unit = match.group(2).rstrip("s")
        relation = match.group(3)
        rest_str = match.group(4).strip()

        base = _resolve_base(rest_str, today)
        if base is None:
            base = _parse_absolute(rest_str)
        if base is None:
            wk_resolved = _parse_weekday(rest_str, today)
            if wk_resolved is not None:
                base = wk_resolved
        if base is None:
            return None

        if relation == "before":
            amount = -amount
        return _add_unit(base, unit, amount)

    match = re.match(r"(\d+)\s+(days?|weeks?|months?|years?)\s+ago$", s)
    if match:
        amount = -int(match.group(1))
        unit = match.group(2).rstrip("s")
        return _add_unit(today, unit, amount)

    match = re.match(
        r"(?:in\s+)?(\d+)\s+(days?|weeks?|months?|years?)(?:\s+from\s+now)?$", s
    )
    if match:
        amount = int(match.group(1))
        unit = match.group(2).rstrip("s")
        return _add_unit(today, unit, amount)

    match = re.match(
        r"(.+?)\s+(\d+)\s+(days?|weeks?|months?|years?)\s+(before|after)$", s
    )
    if match:
        rest_str = match.group(1).strip()
        amount = int(match.group(2))
        unit = match.group(3).rstrip("s")
        relation = match.group(4)

        base = _parse_absolute(rest_str)
        if base is None:
            base = _resolve_base(rest_str, today)
        if base is None:
            wk_resolved = _parse_weekday(rest_str, today)
            if wk_resolved is not None:
                base = wk_resolved
        if base is None:
            return None

        if relation == "before":
            amount = -amount
        return _add_unit(base, unit, amount)

    return None


def parse(s: str, today: date | None = None) -> date:
    if today is None:
        today = date.today()

    result = _parse_absolute(s)
    if result is not None:
        return result

    result = _parse(s, today)
    if result is not None:
        return result

    msg = f"Could not parse date string: {s!r}"
    raise ValueError(msg)
