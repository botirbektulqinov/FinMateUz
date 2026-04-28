from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import create_token, decode_token, hash_password, verify_password
from app.enums import AuditAction, Role
from app.models import AuditLog, Company, CompanyMember, User
from app.schemas import LoginRequest, RegisterRequest, TokenPair
from app.services.categories import create_default_categories


def issue_tokens(user_id: str) -> TokenPair:
    return TokenPair(access_token=create_token(user_id, "access"), refresh_token=create_token(user_id, "refresh"))


def register_user(db: Session, data: RegisterRequest) -> TokenPair:
    existing = db.execute(select(User).where(User.email == data.email.lower())).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email is already registered")
    user = User(email=data.email.lower(), full_name=data.full_name.strip(), hashed_password=hash_password(data.password))
    company = Company(name=data.company_name.strip(), business_type=data.business_type)
    db.add_all([user, company])
    db.flush()
    db.add(CompanyMember(user_id=user.id, company_id=company.id, role=Role.owner))
    create_default_categories(db, company.id)
    db.commit()
    return issue_tokens(user.id)


def login_user(db: Session, data: LoginRequest) -> TokenPair:
    user = db.execute(select(User).where(User.email == data.email.lower())).scalar_one_or_none()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    membership = db.execute(select(CompanyMember).where(CompanyMember.user_id == user.id)).scalar_one_or_none()
    if membership:
        db.add(
            AuditLog(
                company_id=membership.company_id,
                actor_user_id=user.id,
                action=AuditAction.user_login,
                entity_type="user",
                entity_id=user.id,
                metadata_json="{}",
            )
        )
        db.commit()
    return issue_tokens(user.id)


def refresh_tokens(db: Session, refresh_token: str) -> TokenPair:
    try:
        user_id = decode_token(refresh_token, "refresh")
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token") from exc
    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    return issue_tokens(user.id)
