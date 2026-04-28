from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload

from app.enums import AuditAction, Role, TransactionStatus
from app.models import Category, Transaction
from app.schemas import TransactionCreate, TransactionRead, TransactionUpdate
from app.services.audit import record_audit
from app.services.permissions import (
    APPROVE_ROLES,
    CREATE_TRANSACTION_ROLES,
    MANAGE_TRANSACTION_ROLES,
    MembershipContext,
    can_delete_confirmed,
    require_role,
)


def _category_for_transaction(db: Session, ctx: MembershipContext, category_id: str, tx_type: str) -> Category:
    category = db.get(Category, category_id)
    if not category or category.company_id != ctx.company_id or category.deleted_at:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Category is invalid")
    if category.type != tx_type:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Category type does not match transaction")
    return category


def to_read(transaction: Transaction) -> TransactionRead:
    return TransactionRead.model_validate(transaction).model_copy(
        update={"category_name": transaction.category.name if transaction.category else None}
    )


def create_transaction(db: Session, ctx: MembershipContext, data: TransactionCreate) -> Transaction:
    require_role(ctx, CREATE_TRANSACTION_ROLES)
    _category_for_transaction(db, ctx, data.category_id, data.type)
    status_value = TransactionStatus.pending if ctx.role == Role.operator else TransactionStatus.confirmed
    transaction = Transaction(
        company_id=ctx.company_id,
        created_by_user_id=ctx.user.id,
        status=status_value,
        **data.model_dump(),
    )
    db.add(transaction)
    db.flush()
    record_audit(
        db,
        ctx,
        AuditAction.transaction_create,
        "transaction",
        transaction.id,
        {"status": transaction.status, "source": transaction.source},
    )
    db.commit()
    db.refresh(transaction)
    return transaction


def list_transactions(
    db: Session,
    ctx: MembershipContext,
    start_date: date | None = None,
    end_date: date | None = None,
    tx_type: str | None = None,
    category_id: str | None = None,
    status_value: str | None = None,
    search: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[Transaction], int]:
    query = select(Transaction).options(joinedload(Transaction.category)).where(Transaction.company_id == ctx.company_id)
    count_query = select(func.count(Transaction.id)).where(Transaction.company_id == ctx.company_id)
    conditions = []
    if start_date:
        conditions.append(Transaction.transaction_date >= start_date)
    if end_date:
        conditions.append(Transaction.transaction_date <= end_date)
    if tx_type:
        conditions.append(Transaction.type == tx_type)
    if category_id:
        conditions.append(Transaction.category_id == category_id)
    if status_value:
        conditions.append(Transaction.status == status_value)
    else:
        conditions.append(Transaction.status != TransactionStatus.deleted)
    if search:
        like = f"%{search.strip()}%"
        conditions.append(or_(Transaction.note.ilike(like), Category.name.ilike(like)))
        query = query.join(Category)
        count_query = count_query.join(Category)
    for condition in conditions:
        query = query.where(condition)
        count_query = count_query.where(condition)
    total = db.execute(count_query).scalar_one()
    items = list(db.execute(query.order_by(Transaction.transaction_date.desc(), Transaction.created_at.desc()).limit(limit).offset(offset)).scalars())
    return items, total


def update_transaction(db: Session, ctx: MembershipContext, transaction_id: str, data: TransactionUpdate) -> Transaction:
    transaction = db.get(Transaction, transaction_id)
    if not transaction or transaction.company_id != ctx.company_id or transaction.status == TransactionStatus.deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    can_manage = ctx.role in MANAGE_TRANSACTION_ROLES
    can_operator_edit_own_pending = (
        ctx.role == Role.operator
        and transaction.created_by_user_id == ctx.user.id
        and transaction.status == TransactionStatus.pending
    )
    if not can_manage and not can_operator_edit_own_pending:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
    changes = data.model_dump(exclude_unset=True)
    if "category_id" in changes and changes["category_id"]:
        _category_for_transaction(db, ctx, changes["category_id"], transaction.type)
    if "status" in changes:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Use approval endpoints to change status")
    for field, value in changes.items():
        setattr(transaction, field, value)
    record_audit(db, ctx, AuditAction.transaction_update, "transaction", transaction.id, changes)
    db.commit()
    db.refresh(transaction)
    return transaction


def delete_transaction(db: Session, ctx: MembershipContext, transaction_id: str) -> None:
    transaction = db.get(Transaction, transaction_id)
    if not transaction or transaction.company_id != ctx.company_id or transaction.status == TransactionStatus.deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    can_manage = ctx.role in MANAGE_TRANSACTION_ROLES
    can_operator_delete_own_pending = (
        ctx.role == Role.operator
        and transaction.created_by_user_id == ctx.user.id
        and transaction.status == TransactionStatus.pending
    )
    if transaction.status == TransactionStatus.confirmed and not can_delete_confirmed(ctx):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot delete confirmed transaction")
    if transaction.status != TransactionStatus.confirmed and not can_manage and not can_operator_delete_own_pending:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
    transaction.status = TransactionStatus.deleted
    transaction.deleted_at = datetime.now(UTC)
    record_audit(db, ctx, AuditAction.transaction_delete, "transaction", transaction.id, {})
    db.commit()


def approve_transaction(db: Session, ctx: MembershipContext, transaction_id: str, approve: bool) -> Transaction:
    require_role(ctx, APPROVE_ROLES)
    transaction = db.get(Transaction, transaction_id)
    if not transaction or transaction.company_id != ctx.company_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    if transaction.status != TransactionStatus.pending:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Only pending transactions can be reviewed")
    transaction.status = TransactionStatus.confirmed if approve else TransactionStatus.rejected
    record_audit(
        db,
        ctx,
        AuditAction.transaction_approve if approve else AuditAction.transaction_reject,
        "transaction",
        transaction.id,
        {},
    )
    db.commit()
    db.refresh(transaction)
    return transaction


def recent_activity(db: Session, ctx: MembershipContext, limit: int = 10) -> list[Transaction]:
    since = datetime.now(UTC).date() - timedelta(days=30)
    items, _ = list_transactions(db, ctx, start_date=since, limit=limit)
    return items
