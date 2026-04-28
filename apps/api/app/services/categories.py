from datetime import UTC, datetime
from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.enums import AuditAction, TransactionType
from app.models import Category, Transaction
from app.schemas import CategoryCreate, CategoryUpdate
from app.services.audit import record_audit
from app.services.permissions import MANAGE_CATEGORY_ROLES, MembershipContext, require_role

DEFAULT_CATEGORIES: dict[TransactionType, list[tuple[str, str, str]]] = {
    TransactionType.income: [
        ("Sales", "#15803d", "shopping-bag"),
        ("Services", "#0f766e", "briefcase"),
        ("Subscription", "#2563eb", "repeat"),
        ("Debt repayment", "#7c3aed", "hand-coins"),
        ("Investment", "#059669", "trending-up"),
        ("Other income", "#4b5563", "circle-plus"),
    ],
    TransactionType.expense: [
        ("Salary", "#b91c1c", "users"),
        ("Rent", "#c2410c", "building"),
        ("Logistics", "#d97706", "truck"),
        ("Marketing", "#db2777", "megaphone"),
        ("Office", "#475569", "briefcase-business"),
        ("Inventory", "#9333ea", "boxes"),
        ("Utilities", "#0891b2", "plug"),
        ("Tax", "#7f1d1d", "receipt"),
        ("Internet and phone", "#1d4ed8", "wifi"),
        ("Food", "#65a30d", "utensils"),
        ("Transport", "#ea580c", "bus"),
        ("Debt payment", "#6d28d9", "wallet-cards"),
        ("Other expense", "#4b5563", "circle-minus"),
    ],
}


def create_default_categories(db: Session, company_id: str) -> None:
    for category_type, items in DEFAULT_CATEGORIES.items():
        for name, color, icon in items:
            db.add(
                Category(
                    company_id=company_id,
                    name=name,
                    type=category_type,
                    color=color,
                    icon=icon,
                    is_default=True,
                )
            )


def list_categories(db: Session, ctx: MembershipContext, category_type: TransactionType | None = None) -> list[Category]:
    query = select(Category).where(Category.company_id == ctx.company_id, Category.deleted_at.is_(None))
    if category_type:
        query = query.where(Category.type == category_type)
    return list(db.execute(query.order_by(Category.type, Category.is_default.desc(), Category.name)).scalars())


def create_category(db: Session, ctx: MembershipContext, data: CategoryCreate) -> Category:
    require_role(ctx, MANAGE_CATEGORY_ROLES)
    category = Category(company_id=ctx.company_id, **data.model_dump(), is_default=False)
    db.add(category)
    db.flush()
    record_audit(db, ctx, AuditAction.category_create, "category", category.id, {"name": category.name})
    db.commit()
    db.refresh(category)
    return category


def update_category(db: Session, ctx: MembershipContext, category_id: str, data: CategoryUpdate) -> Category:
    require_role(ctx, MANAGE_CATEGORY_ROLES)
    category = db.get(Category, category_id)
    if not category or category.company_id != ctx.company_id or category.deleted_at:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(category, field, value)
    record_audit(db, ctx, AuditAction.category_update, "category", category.id, data.model_dump(exclude_unset=True))
    db.commit()
    db.refresh(category)
    return category


def delete_category(db: Session, ctx: MembershipContext, category_id: str) -> None:
    require_role(ctx, MANAGE_CATEGORY_ROLES)
    category = db.get(Category, category_id)
    if not category or category.company_id != ctx.company_id or category.deleted_at:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    usage_count = db.execute(
        select(func.count(Transaction.id)).where(Transaction.company_id == ctx.company_id, Transaction.category_id == category_id)
    ).scalar_one()
    if usage_count:
        category.deleted_at = datetime.now(UTC)
    else:
        db.delete(category)
    record_audit(db, ctx, AuditAction.category_delete, "category", category_id, {"soft_deleted": bool(usage_count)})
    db.commit()
