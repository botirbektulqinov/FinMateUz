from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.enums import Role, TransactionSource, TransactionStatus, TransactionType
from app.schemas.common import clean_text


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TelegramLinkCode(BaseModel):
    link_code: str
    command: str
    expires_in_minutes: int


class TelegramLinkRequest(BaseModel):
    telegram_user_id: int
    link_code: str = Field(min_length=20)


class TelegramLinkResponse(BaseModel):
    linked: bool
    company_id: str
    user_id: str
    role: Role


class LinkedTelegramAccount(BaseModel):
    telegram_user_id: int
    access_token: str
    company_id: str
    user_id: str
    role: Role


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class RegisterRequest(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=160)
    password: str = Field(min_length=8, max_length=128)
    company_name: str = Field(min_length=2, max_length=180)
    business_type: str | None = Field(default=None, max_length=120)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserRead(BaseModel):
    id: str
    email: EmailStr
    full_name: str

    model_config = {"from_attributes": True}


class CompanyCreate(BaseModel):
    name: str = Field(min_length=2, max_length=180)
    business_type: str | None = Field(default=None, max_length=120)
    default_currency: str = Field(default="UZS", min_length=3, max_length=3)

    @field_validator("name", "business_type")
    @classmethod
    def sanitize(cls, value: str | None) -> str | None:
        return clean_text(value, 180)

    @field_validator("default_currency")
    @classmethod
    def currency_upper(cls, value: str) -> str:
        return value.upper()


class CompanyUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=180)
    business_type: str | None = Field(default=None, max_length=120)

    @field_validator("name", "business_type")
    @classmethod
    def sanitize(cls, value: str | None) -> str | None:
        return clean_text(value, 180)


class CompanyRead(BaseModel):
    id: str
    name: str
    business_type: str | None
    default_currency: str
    role: Role | None = None

    model_config = {"from_attributes": True}


class MemberRead(BaseModel):
    id: str
    user_id: str
    email: EmailStr
    full_name: str
    role: Role
    can_delete_confirmed: bool


class CategoryCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    type: TransactionType
    color: str | None = Field(default=None, max_length=24)
    icon: str | None = Field(default=None, max_length=48)

    @field_validator("name", "color", "icon")
    @classmethod
    def sanitize(cls, value: str | None) -> str | None:
        return clean_text(value, 120)


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    color: str | None = Field(default=None, max_length=24)
    icon: str | None = Field(default=None, max_length=48)

    @field_validator("name", "color", "icon")
    @classmethod
    def sanitize(cls, value: str | None) -> str | None:
        return clean_text(value, 120)


class CategoryRead(BaseModel):
    id: str
    company_id: str
    name: str
    type: TransactionType
    color: str | None
    icon: str | None
    is_default: bool

    model_config = {"from_attributes": True}


class TransactionCreate(BaseModel):
    type: TransactionType
    amount: Decimal = Field(gt=0, max_digits=18, decimal_places=2)
    currency: str = Field(default="UZS", min_length=3, max_length=3)
    category_id: str
    transaction_date: date
    note: str | None = Field(default=None, max_length=500)
    source: TransactionSource = TransactionSource.dashboard
    raw_text: str | None = Field(default=None, max_length=1000)
    confidence_score: Decimal | None = Field(default=None, ge=0, le=1)

    @field_validator("note", "raw_text")
    @classmethod
    def sanitize(cls, value: str | None) -> str | None:
        return clean_text(value, 1000)

    @field_validator("currency")
    @classmethod
    def currency_upper(cls, value: str) -> str:
        return value.upper()


class TransactionUpdate(BaseModel):
    amount: Decimal | None = Field(default=None, gt=0, max_digits=18, decimal_places=2)
    category_id: str | None = None
    transaction_date: date | None = None
    note: str | None = Field(default=None, max_length=500)
    status: TransactionStatus | None = None

    @field_validator("note")
    @classmethod
    def sanitize(cls, value: str | None) -> str | None:
        return clean_text(value, 500)


class TransactionRead(BaseModel):
    id: str
    company_id: str
    created_by_user_id: str
    type: TransactionType
    amount: Decimal
    currency: str
    category_id: str
    category_name: str | None = None
    transaction_date: date
    note: str | None
    source: TransactionSource
    raw_text: str | None
    confidence_score: Decimal | None
    status: TransactionStatus
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None

    model_config = {"from_attributes": True}


class TransactionList(BaseModel):
    items: list[TransactionRead]
    total: int


class ReportSummary(BaseModel):
    month_income: Decimal
    month_expenses: Decimal
    net_cash_flow: Decimal
    previous_month_income: Decimal
    previous_month_expenses: Decimal
    income_change_percent: Decimal | None
    expense_change_percent: Decimal | None
    pending_approval_count: int


class OverviewReport(BaseModel):
    summary: ReportSummary
    recent_transactions: list[TransactionRead]


class TimeSeriesPoint(BaseModel):
    period: str
    income: Decimal
    expense: Decimal
    net: Decimal


class CategoryBreakdownPoint(BaseModel):
    category_id: str
    category_name: str
    total: Decimal


class DashboardReport(BaseModel):
    summary: ReportSummary
    income_vs_expenses: list[TimeSeriesPoint]
    expense_breakdown: list[CategoryBreakdownPoint]
    income_breakdown: list[CategoryBreakdownPoint]
    top_expense_categories: list[CategoryBreakdownPoint]
    top_income_categories: list[CategoryBreakdownPoint]
    recent_transactions: list[TransactionRead]


class AuditLogRead(BaseModel):
    id: str
    company_id: str
    actor_user_id: str | None
    action: str
    entity_type: str
    entity_id: str
    metadata_json: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
