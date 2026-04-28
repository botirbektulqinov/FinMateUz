from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.enums import Role
from app.models import Company, CompanyMember
from app.schemas import CompanyCreate, CompanyRead, CompanyUpdate
from app.services.categories import create_default_categories
from app.services.permissions import MANAGE_MEMBER_ROLES, MembershipContext, require_role


def to_company_read(company: Company, role: Role | None = None) -> CompanyRead:
    return CompanyRead(
        id=company.id,
        name=company.name,
        business_type=company.business_type,
        default_currency=company.default_currency,
        role=role,
    )


def create_company(db: Session, user_id: str, data: CompanyCreate) -> Company:
    company = Company(**data.model_dump())
    db.add(company)
    db.flush()
    db.add(CompanyMember(company_id=company.id, user_id=user_id, role=Role.owner))
    create_default_categories(db, company.id)
    db.commit()
    db.refresh(company)
    return company


def get_current_company(db: Session, ctx: MembershipContext) -> Company:
    company = db.get(Company, ctx.company_id)
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    return company


def update_current_company(db: Session, ctx: MembershipContext, data: CompanyUpdate) -> Company:
    require_role(ctx, MANAGE_MEMBER_ROLES)
    company = get_current_company(db, ctx)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(company, field, value)
    db.commit()
    db.refresh(company)
    return company
