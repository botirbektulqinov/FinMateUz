from datetime import date
from decimal import Decimal

from bot.parsers import detect_intent, parse_amount, parse_date, parse_message


def test_parse_uzbek_expense_with_scaled_amount_and_category() -> None:
    parsed = parse_message("bugun 250 ming logistika uchun ketdi", today=date(2026, 4, 27))
    assert parsed.intent == "create_expense"
    assert parsed.amount.value == Decimal("250000.00")
    assert parsed.type == "expense"
    assert parsed.category_name == "Logistics"
    assert parsed.transaction_date == date(2026, 4, 27)
    assert parsed.missing_fields == []


def test_parse_yesterday_income_million_phrase() -> None:
    parsed = parse_message("kecha 1 million 200 ming tushdi sayt uchun", today=date(2026, 4, 27))
    assert parsed.intent == "create_income"
    assert parsed.amount.value == Decimal("1200000.00")
    assert parsed.note == "sayt uchun"
    assert parsed.type == "income"
    assert parsed.category_name == "Services"
    assert parsed.transaction_date == date(2026, 4, 26)


def test_ambiguous_expense_asks_for_category() -> None:
    parsed = parse_message("50 ming ketdi", today=date(2026, 4, 27))
    assert parsed.intent == "create_expense"
    assert parsed.amount.value == Decimal("50000.00")
    assert "category" in parsed.missing_fields


def test_report_and_last_transaction_intents() -> None:
    assert parse_message("bu oy qancha xarajat qildik?").intent == "get_report"
    assert parse_message("logistikaga qancha ketdi?").intent == "get_report"
    assert parse_message("oxirgisini o‘chir").intent == "delete_last_transaction"
    assert parse_message("oxirgisini 90 ming qil").intent == "edit_last_transaction"


def test_amount_parser_formats_and_currency() -> None:
    assert parse_amount("50000").value == Decimal("50000.00")
    assert parse_amount("50 000").value == Decimal("50000")
    assert parse_amount("50 ming").value == Decimal("50000.00")
    assert parse_amount("1 mln").value == Decimal("1000000.00")
    assert parse_amount("1.2 mln").value == Decimal("1200000.00")
    amount = parse_amount("100 dollar")
    assert amount.value == Decimal("100.00")
    assert amount.currency == "USD"


def test_date_parser_relative_periods_and_future_confirmation() -> None:
    today = date(2026, 4, 27)
    assert parse_date("bugun", today).value == today
    assert parse_date("kecha", today).value == date(2026, 4, 26)
    assert parse_date("bu hafta", today).period == "current_week"
    assert parse_date("bu oy", today).period == "current_month"
    assert parse_date("2026-04-20", today).value == date(2026, 4, 20)
    future = parse_date("ertaga", today)
    assert future.value == date(2026, 4, 28)
    assert future.needs_future_confirmation is True


def test_future_transaction_needs_confirmation() -> None:
    parsed = parse_message("ertaga 250 ming logistika uchun ketdi", today=date(2026, 4, 27))
    assert parsed.transaction_date == date(2026, 4, 28)
    assert parsed.needs_confirmation is True


def test_intent_detection() -> None:
    assert detect_intent("bugun 250 ming logistika uchun ketdi") == "create_expense"
    assert detect_intent("kecha 1 mln tushdi") == "create_income"
    assert detect_intent("kategoriya qo'sh marketing") == "create_category"
    assert detect_intent("nima gap?") == "ask_question"
