from datetime import date
from decimal import Decimal
import re

from bot.parsers.amounts import parse_amount
from bot.parsers.categories import infer_category
from bot.parsers.dates import parse_date
from bot.parsers.intents import detect_intent, detect_report_kind, infer_type
from bot.parsers.models import Intent, ParsedMessage, TransactionType
from bot.parsers.text import normalize


def _note_from_text(text: str) -> str | None:
    normalized = normalize(text)
    cleaned = re.sub(r"\bbugun\b|\bkecha\b|\bertaga\b|\bbu oy\b|\bbu hafta\b", " ", normalized)
    cleaned = re.sub(r"\d+(?:[.,]\d+)?(?:\s\d{3})*|million|mln|ming|usd|dollar|so'm|so‘m|uzs", " ", cleaned)
    cleaned = re.sub(r"\bketdi\b|\btushdi\b|\bkeldi\b|\bxarajat\b|\bkirim\b|\bchiqim\b", " ", cleaned)
    return " ".join(cleaned.split()) or None


def parse_message(text: str, today: date | None = None) -> ParsedMessage:
    normalized = normalize(text)
    amount = parse_amount(normalized)
    tx_type, type_confidence = infer_type(normalized)
    category_key, category_name, category_confidence = infer_category(normalized, tx_type)
    parsed_date = parse_date(normalized, today)
    intent = detect_intent(normalized)
    if intent == Intent.create_income:
        tx_type = TransactionType.income
    if intent == Intent.create_expense:
        tx_type = TransactionType.expense
    missing: list[str] = []
    if intent in {Intent.create_income, Intent.create_expense}:
        if amount is None:
            missing.append("amount")
        if tx_type is None:
            missing.append("type")
        if category_name is None:
            missing.append("category")
    confidence = min(type_confidence, category_confidence)
    if amount:
        confidence += Decimal("0.08")
    if parsed_date.needs_future_confirmation:
        confidence -= Decimal("0.15")
    confidence = max(Decimal("0"), min(confidence, Decimal("0.95")))
    return ParsedMessage(
        intent=intent,
        amount=amount,
        type=tx_type,
        category_key=category_key,
        category_name=category_name,
        transaction_date=parsed_date.value,
        period=parsed_date.period,
        note=_note_from_text(normalized),
        report_kind=detect_report_kind(normalized, category_key) if intent == Intent.get_report else None,
        confidence=confidence,
        missing_fields=missing,
        needs_confirmation=parsed_date.needs_future_confirmation or confidence < Decimal("0.70"),
        raw_text=text,
    )
