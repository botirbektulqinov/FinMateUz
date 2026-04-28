from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from enum import StrEnum


class Intent(StrEnum):
    create_income = "create_income"
    create_expense = "create_expense"
    get_report = "get_report"
    ask_question = "ask_question"
    edit_last_transaction = "edit_last_transaction"
    delete_last_transaction = "delete_last_transaction"
    create_category = "create_category"
    unknown = "unknown"


class TransactionType(StrEnum):
    income = "income"
    expense = "expense"


class ReportKind(StrEnum):
    overview = "overview"
    expense = "expense"
    income = "income"
    category = "category"


@dataclass(frozen=True)
class ParsedAmount:
    value: Decimal
    currency: str = "UZS"


@dataclass(frozen=True)
class ParsedDate:
    value: date | None
    period: str | None = None
    needs_future_confirmation: bool = False


@dataclass(frozen=True)
class ParsedMessage:
    intent: Intent
    amount: ParsedAmount | None = None
    type: TransactionType | None = None
    category_key: str | None = None
    category_name: str | None = None
    transaction_date: date | None = None
    period: str | None = None
    note: str | None = None
    report_kind: ReportKind | None = None
    confidence: Decimal = Decimal("0")
    missing_fields: list[str] = field(default_factory=list)
    needs_confirmation: bool = False
    raw_text: str = ""
