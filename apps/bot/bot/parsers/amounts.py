from decimal import Decimal, InvalidOperation
import re

from bot.parsers.models import ParsedAmount
from bot.parsers.text import normalize

SCALE_WORDS = {
    "ming": Decimal("1000"),
    "k": Decimal("1000"),
    "mln": Decimal("1000000"),
    "m": Decimal("1000000"),
    "million": Decimal("1000000"),
    "млн": Decimal("1000000"),
}

CURRENCY_WORDS = {
    "usd": "USD",
    "dollar": "USD",
    "dollor": "USD",
    "$": "USD",
    "sum": "UZS",
    "so'm": "UZS",
    "so‘m": "UZS",
    "uzs": "UZS",
}


def _decimal(token: str) -> Decimal | None:
    try:
        return Decimal(token.replace(" ", "").replace(",", "."))
    except InvalidOperation:
        return None


def parse_amount(text: str) -> ParsedAmount | None:
    normalized = normalize(text)
    currency = "UZS"
    for word, code in CURRENCY_WORDS.items():
        if re.search(rf"(^|\s){re.escape(word)}(\s|$)", normalized):
            currency = code
            break

    compact_match = re.search(r"(?<!\d)(\d{1,3}(?:\s\d{3})+)(?!\d)", normalized)
    if compact_match:
        value = _decimal(compact_match.group(1))
        return ParsedAmount(value=value, currency=currency) if value and value > 0 else None

    tokens = re.findall(r"\d+(?:[.,]\d+)?|million|mln|ming|k|m|млн", normalized)
    if not tokens:
        return None

    total = Decimal("0")
    last_number: Decimal | None = None
    saw_scale = False
    for token in tokens:
        number = _decimal(token)
        if number is not None:
            last_number = number
            continue
        scale = SCALE_WORDS.get(token)
        if scale and last_number is not None:
            total += last_number * scale
            saw_scale = True
            last_number = None

    if last_number is not None:
        if currency != "UZS":
            total += last_number
        else:
            total += last_number if saw_scale or last_number >= 1000 else last_number * Decimal("1000")
    if total <= 0:
        return None
    return ParsedAmount(value=total.quantize(Decimal("0.01")), currency=currency)
