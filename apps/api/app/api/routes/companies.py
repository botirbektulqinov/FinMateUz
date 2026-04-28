from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import get_company_context, get_current_user
from app.enums import Role
from app.models import Company, CompanyMember, User
from app.schemas import CompanyCreate, CompanyRead, CompanyUpdate, MemberRead
from app.services import companies as service
from app.services.permissions import MembershipContext

router = APIRouter(prefix="/companies", tags=["companies"])


@router.post("", response_model=CompanyRead)
def create_company(data: CompanyCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> CompanyRead:
    company = service.create_company(db, user.id, data)
    return service.to_company_read(company, role=Role.owner)


@router.get("/current", response_model=CompanyRead)
def current_company(ctx: MembershipContext = Depends(get_company_context), db: Session = Depends(get_db)) -> CompanyRead:
    company = service.get_current_company(db, ctx)
    return service.to_company_read(company, role=ctx.role)


@router.patch("/current", response_model=CompanyRead)
def update_company(
    data: CompanyUpdate,
    ctx: MembershipContext = Depends(get_company_context),
    db: Session = Depends(get_db),
) -> CompanyRead:
    company = service.update_current_company(db, ctx, data)
    return service.to_company_read(company, role=ctx.role)


@router.get("/me", response_model=list[CompanyRead])
def my_companies(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[CompanyRead]:
    rows = db.execute(
        select(Company, CompanyMember.role)
        .join(CompanyMember, CompanyMember.company_id == Company.id)
        .where(CompanyMember.user_id == user.id)
        .order_by(Company.created_at)
    ).all()
    return [service.to_company_read(company, role=role) for company, role in rows]


@router.get("/members", response_model=list[MemberRead])
def company_members(ctx: MembershipContext = Depends(get_company_context), db: Session = Depends(get_db)) -> list[MemberRead]:
    rows = db.execute(
        select(CompanyMember, User)
        .join(User, User.id == CompanyMember.user_id)
        .where(CompanyMember.company_id == ctx.company_id)
        .order_by(CompanyMember.created_at)
    ).all()
    return [
        MemberRead(
            id=member.id,
            user_id=user.id,
            email=user.email,
            full_name=user.full_name,
            role=member.role,
            can_delete_confirmed=member.can_delete_confirmed,
        )
        for member, user in rows
    ]
