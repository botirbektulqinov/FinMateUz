from datetime import date, datetime
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import BigInteger, Boolean, Date, DateTime, ForeignKey, Index, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.enums import Role, TransactionSource, TransactionStatus, TransactionType


def uuid_str() -> str:
    return str(uuid4())


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(160), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    memberships: Mapped[list["CompanyMember"]] = relationship(back_populates="user")


class Company(TimestampMixin, Base):
    __tablename__ = "companies"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    name: Mapped[str] = mapped_column(String(180), nullable=False)
    business_type: Mapped[str | None] = mapped_column(String(120))
    default_currency: Mapped[str] = mapped_column(String(3), default="UZS", nullable=False)

    members: Mapped[list["CompanyMember"]] = relationship(back_populates="company", cascade="all, delete-orphan")
    categories: Mapped[list["Category"]] = relationship(back_populates="company")


class CompanyMember(TimestampMixin, Base):
    __tablename__ = "company_members"
    __table_args__ = (UniqueConstraint("company_id", "user_id", name="uq_company_member"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), index=True, nullable=False)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    role: Mapped[Role] = mapped_column(String(32), nullable=False)
    can_delete_confirmed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    company: Mapped[Company] = relationship(back_populates="members")
    user: Mapped[User] = relationship(back_populates="memberships")


class Category(TimestampMixin, Base):
    __tablename__ = "categories"
    __table_args__ = (
        UniqueConstraint("company_id", "name", "type", name="uq_category_company_name_type"),
        Index("ix_categories_company_type", "company_id", "type"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    type: Mapped[TransactionType] = mapped_column(String(16), nullable=False)
    color: Mapped[str | None] = mapped_column(String(24))
    icon: Mapped[str | None] = mapped_column(String(48))
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    company: Mapped[Company] = relationship(back_populates="categories")
    transactions: Mapped[list["Transaction"]] = relationship(back_populates="category")


class Transaction(TimestampMixin, Base):
    __tablename__ = "transactions"
    __table_args__ = (
        Index("ix_transactions_company_date", "company_id", "transaction_date"),
        Index("ix_transactions_company_status", "company_id", "status"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), index=True, nullable=False)
    created_by_user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    type: Mapped[TransactionType] = mapped_column(String(16), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="UZS", nullable=False)
    category_id: Mapped[str] = mapped_column(ForeignKey("categories.id"), index=True, nullable=False)
    transaction_date: Mapped[date] = mapped_column(Date, nullable=False)
    note: Mapped[str | None] = mapped_column(Text)
    source: Mapped[TransactionSource] = mapped_column(String(24), nullable=False)
    raw_text: Mapped[str | None] = mapped_column(Text)
    confidence_score: Mapped[Decimal | None] = mapped_column(Numeric(4, 3))
    status: Mapped[TransactionStatus] = mapped_column(String(24), default=TransactionStatus.confirmed, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    category: Mapped[Category] = relationship(back_populates="transactions")
    creator: Mapped[User] = relationship()


class AuditLog(Base):
    __tablename__ = "audit_logs"
    __table_args__ = (Index("ix_audit_logs_company_entity", "company_id", "entity_type", "entity_id"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), index=True, nullable=False)
    actor_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), index=True)
    action: Mapped[str] = mapped_column(String(64), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(64), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(36), nullable=False)
    metadata_json: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class TelegramAccount(TimestampMixin, Base):
    __tablename__ = "telegram_accounts"
    __table_args__ = (UniqueConstraint("telegram_user_id", name="uq_telegram_user"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    telegram_user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    pending_state_json: Mapped[str | None] = mapped_column(Text)
    last_transaction_id: Mapped[str | None] = mapped_column(ForeignKey("transactions.id"))
