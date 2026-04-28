from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import get_current_user
from app.models import User
from app.schemas import LoginRequest, RefreshTokenRequest, RegisterRequest, TokenPair, UserRead
from app.services import auth as service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenPair, status_code=status.HTTP_201_CREATED)
def register(data: RegisterRequest, db: Session = Depends(get_db)) -> TokenPair:
    return service.register_user(db, data)


@router.post("/login", response_model=TokenPair)
def login(data: LoginRequest, db: Session = Depends(get_db)) -> TokenPair:
    return service.login_user(db, data)


@router.post("/refresh", response_model=TokenPair)
def refresh(data: RefreshTokenRequest, db: Session = Depends(get_db)) -> TokenPair:
    return service.refresh_tokens(db, data.refresh_token)


@router.get("/me", response_model=UserRead)
def me(user: User = Depends(get_current_user)) -> User:
    return user
