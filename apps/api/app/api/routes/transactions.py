from datetime import date

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import get_company_context
from app.enums import TransactionStatus, TransactionType
from app.schemas import TransactionCreate, TransactionList, TransactionRead, TransactionUpdate
from app.services import transactions as service
from app.services.permissions import MembershipContext

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post("", response_model=TransactionRead, status_code=status.HTTP_201_CREATED)
def create_transaction(data: TransactionCreate, ctx: MembershipContext = Depends(get_company_context), db: Session = Depends(get_db)):
    return service.to_read(service.create_transaction(db, ctx, data))


@router.get("", response_model=TransactionList)
def list_transactions(
    start_date: date | None = None,
    end_date: date | None = None,
    type: TransactionType | None = None,
    category_id: str | None = None,
    status_value: TransactionStatus | None = Query(default=None, alias="status"),
    search: str | None = None,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    ctx: MembershipContext = Depends(get_company_context),
    db: Session = Depends(get_db),
) -> TransactionList:
    items, total = service.list_transactions(
        db, ctx, start_date, end_date, type, category_id, status_value, search, limit, offset
    )
    return TransactionList(items=[service.to_read(item) for item in items], total=total)


@router.get("/recent", response_model=list[TransactionRead])
def recent_activity(ctx: MembershipContext = Depends(get_company_context), db: Session = Depends(get_db)):
    return [service.to_read(item) for item in service.recent_activity(db, ctx)]


@router.patch("/{transaction_id}", response_model=TransactionRead)
def update_transaction(
    transaction_id: str,
    data: TransactionUpdate,
    ctx: MembershipContext = Depends(get_company_context),
    db: Session = Depends(get_db),
):
    return service.to_read(service.update_transaction(db, ctx, transaction_id, data))


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(transaction_id: str, ctx: MembershipContext = Depends(get_company_context), db: Session = Depends(get_db)):
    service.delete_transaction(db, ctx, transaction_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{transaction_id}/approve", response_model=TransactionRead)
def approve_transaction(transaction_id: str, ctx: MembershipContext = Depends(get_company_context), db: Session = Depends(get_db)):
    return service.to_read(service.approve_transaction(db, ctx, transaction_id, approve=True))


@router.post("/{transaction_id}/reject", response_model=TransactionRead)
def reject_transaction(transaction_id: str, ctx: MembershipContext = Depends(get_company_context), db: Session = Depends(get_db)):
    return service.to_read(service.approve_transaction(db, ctx, transaction_id, approve=False))
