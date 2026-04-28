from fastapi import Depends, Header, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.db import get_db
from app.models import CompanyMember, User
from app.services.permissions import MembershipContext

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    try:
        user_id = decode_token(token, "access")
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication") from exc
    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication")
    return user


def get_company_context(
    x_company_id: str = Header(alias="X-Company-Id"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MembershipContext:
    member = db.execute(
        select(CompanyMember).where(CompanyMember.company_id == x_company_id, CompanyMember.user_id == user.id)
    ).scalar_one_or_none()
    if not member:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Company access denied")
    return MembershipContext(user=user, member=member)
