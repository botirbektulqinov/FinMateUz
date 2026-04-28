from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import get_company_context
from app.enums import TransactionType
from app.schemas import CategoryCreate, CategoryRead, CategoryUpdate
from app.services import categories as service
from app.services.permissions import MembershipContext

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=list[CategoryRead])
def list_categories(
    type: TransactionType | None = None,
    ctx: MembershipContext = Depends(get_company_context),
    db: Session = Depends(get_db),
) -> list:
    return service.list_categories(db, ctx, type)


@router.post("", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
def create_category(data: CategoryCreate, ctx: MembershipContext = Depends(get_company_context), db: Session = Depends(get_db)):
    return service.create_category(db, ctx, data)


@router.patch("/{category_id}", response_model=CategoryRead)
def update_category(
    category_id: str,
    data: CategoryUpdate,
    ctx: MembershipContext = Depends(get_company_context),
    db: Session = Depends(get_db),
):
    return service.update_category(db, ctx, category_id, data)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: str, ctx: MembershipContext = Depends(get_company_context), db: Session = Depends(get_db)):
    service.delete_category(db, ctx, category_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
