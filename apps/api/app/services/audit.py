import json
from typing import Any
from sqlalchemy.orm import Session

from app.models import AuditLog
from app.services.permissions import MembershipContext


def record_audit(
    db: Session,
    ctx: MembershipContext,
    action: str,
    entity_type: str,
    entity_id: str,
    metadata: dict[str, Any] | None = None,
) -> AuditLog:
    log = AuditLog(
        company_id=ctx.company_id,
        actor_user_id=ctx.user.id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        metadata_json=json.dumps(metadata or {}, default=str),
    )
    db.add(log)
    return log
