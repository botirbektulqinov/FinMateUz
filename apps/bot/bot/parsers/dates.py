from datetime import date, timedelta
import re

from bot.parsers.models import ParsedDate
from bot.parsers.text import normalize


def parse_date(text: str, today: date | None = None) -> ParsedDate:
    today = today or date.today()
    normalized = normalize(text)
    explicit = re.search(r"\b(20\d{2}-\d{2}-\d{2})\b", normalized)
    if explicit:
        try:
            parsed = date.fromisoformat(explicit.group(1))
        except ValueError:
            return ParsedDate(value=today)
        return ParsedDate(value=parsed, needs_future_confirmation=parsed > today)
    if "ertaga" in normalized:
        return ParsedDate(value=today + timedelta(days=1), needs_future_confirmation=True)
    if "kecha" in normalized:
        return ParsedDate(value=today - timedelta(days=1))
    if "bugun" in normalized:
        return ParsedDate(value=today)
    if "bu hafta" in normalized or "this week" in normalized:
        return ParsedDate(value=None, period="current_week")
    if "bu oy" in normalized or "this month" in normalized:
        return ParsedDate(value=None, period="current_month")
    return ParsedDate(value=today)
