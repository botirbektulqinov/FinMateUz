from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import get_company_context
from app.models import AuditLog
from app.schemas import AuditLogRead
from app.services.permissions import MembershipContext

router = APIRouter(prefix="/audit-logs", tags=["audit"])


@router.get("", response_model=list[AuditLogRead])
def list_audit_logs(
    limit: int = Query(default=50, ge=1, le=200),
    ctx: MembershipContext = Depends(get_company_context),
    db: Session = Depends(get_db),
):
    return list(
        db.execute(
            select(AuditLog)
            .where(AuditLog.company_id == ctx.company_id)
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
        ).scalars()
    )
