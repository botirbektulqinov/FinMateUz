from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import create_telegram_link_token, create_token, decode_token_payload
from app.db import get_db
from app.deps import get_company_context
from app.models import CompanyMember, TelegramAccount, User
from app.schemas import LinkedTelegramAccount, TelegramLinkCode, TelegramLinkRequest, TelegramLinkResponse
from app.services.permissions import MembershipContext

router = APIRouter(prefix="/bot", tags=["bot"])
LINK_CODE_TTL_MINUTES = 15


def verify_bot_api_token(x_bot_api_token: str = Header(alias="X-Bot-Api-Token")) -> None:
    if x_bot_api_token != get_settings().bot_api_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid bot service token")


@router.get("/link-code", response_model=TelegramLinkCode)
def create_link_code(ctx: MembershipContext = Depends(get_company_context)) -> TelegramLinkCode:
    code = create_telegram_link_token(ctx.user.id, ctx.company_id, expires_minutes=LINK_CODE_TTL_MINUTES)
    return TelegramLinkCode(
        link_code=code,
        command=f"/link {code}",
        expires_in_minutes=LINK_CODE_TTL_MINUTES,
    )


@router.post("/link", response_model=TelegramLinkResponse, dependencies=[Depends(verify_bot_api_token)])
def link_telegram_account(data: TelegramLinkRequest, db: Session = Depends(get_db)) -> TelegramLinkResponse:
    try:
        payload = decode_token_payload(data.link_code, "telegram_link")
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired Telegram link code") from exc

    user_id = str(payload["sub"])
    company_id = str(payload.get("company_id") or "")
    member = db.execute(
        select(CompanyMember).where(CompanyMember.user_id == user_id, CompanyMember.company_id == company_id)
    ).scalar_one_or_none()
    if not member or not db.get(User, user_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Telegram link code")

    account = db.execute(
        select(TelegramAccount).where(TelegramAccount.telegram_user_id == data.telegram_user_id)
    ).scalar_one_or_none()
    if not account:
        account = TelegramAccount(telegram_user_id=data.telegram_user_id, user_id=user_id, company_id=company_id)
        db.add(account)
    else:
        account.user_id = user_id
        account.company_id = company_id
    db.commit()

    return TelegramLinkResponse(linked=True, company_id=company_id, user_id=user_id, role=member.role)


@router.get(
    "/telegram-accounts/{telegram_user_id}",
    response_model=LinkedTelegramAccount,
    dependencies=[Depends(verify_bot_api_token)],
)
def get_linked_telegram_account(telegram_user_id: int, db: Session = Depends(get_db)) -> LinkedTelegramAccount:
    account = db.execute(
        select(TelegramAccount).where(TelegramAccount.telegram_user_id == telegram_user_id)
    ).scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Telegram account is not linked")

    member = db.execute(
        select(CompanyMember).where(CompanyMember.user_id == account.user_id, CompanyMember.company_id == account.company_id)
    ).scalar_one_or_none()
    user = db.get(User, account.user_id)
    if not member or not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Telegram account is not linked")

    return LinkedTelegramAccount(
        telegram_user_id=telegram_user_id,
        access_token=create_token(account.user_id, "access"),
        company_id=account.company_id,
        user_id=account.user_id,
        role=member.role,
    )
