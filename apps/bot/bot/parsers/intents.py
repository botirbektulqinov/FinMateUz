from decimal import Decimal

from bot.parsers.amounts import parse_amount
from bot.parsers.models import Intent, ReportKind, TransactionType
from bot.parsers.text import normalize

EXPENSE_WORDS = {"ketdi", "xarajat", "xarajatmi", "toladik", "to'ladik", "berdik", "chiqim", "chiqdi", "расход"}
INCOME_WORDS = {"tushdi", "keldi", "daromad", "sotdik", "kirim", "приход", "доход"}
REPORT_WORDS = {"qancha", "hisobot", "qoldi", "qildik", "report", "bo'yicha", "bo‘yicha"}
DELETE_LAST_WORDS = {"ochir", "o'chir", "o‘chir", "delete", "bekor"}
EDIT_LAST_WORDS = {"qil", "almashtir", "ozgartir", "o'zgartir", "o‘zgartir"}


def infer_type(text: str) -> tuple[TransactionType | None, Decimal]:
    normalized = normalize(text)
    if any(word in normalized for word in EXPENSE_WORDS):
        return TransactionType.expense, Decimal("0.86")
    if any(word in normalized for word in INCOME_WORDS):
        return TransactionType.income, Decimal("0.86")
    return None, Decimal("0.20")


def detect_report_kind(text: str, category_key: str | None = None) -> ReportKind:
    normalized = normalize(text)
    if category_key:
        return ReportKind.category
    if "kirim" in normalized or "daromad" in normalized:
        return ReportKind.income
    if "xarajat" in normalized or "chiqim" in normalized or "ketdi" in normalized:
        return ReportKind.expense
    return ReportKind.overview


def detect_intent(text: str) -> Intent:
    normalized = normalize(text)
    if "kategoriya" in normalized and ("yarat" in normalized or "qosh" in normalized or "qo'sh" in normalized):
        return Intent.create_category
    if "oxirgi" in normalized or "oxirgisini" in normalized:
        if any(word in normalized for word in DELETE_LAST_WORDS):
            return Intent.delete_last_transaction
        if parse_amount(normalized) and any(word in normalized for word in EDIT_LAST_WORDS):
            return Intent.edit_last_transaction
    if any(word in normalized for word in REPORT_WORDS) and not parse_amount(normalized):
        return Intent.get_report
    tx_type, _ = infer_type(normalized)
    if tx_type == TransactionType.income:
        return Intent.create_income
    if tx_type == TransactionType.expense:
        return Intent.create_expense
    if "?" in normalized:
        return Intent.ask_question
    return Intent.unknown
