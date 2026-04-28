from dataclasses import dataclass
from fastapi import HTTPException, status

from app.enums import Role
from app.models import CompanyMember, User


@dataclass(frozen=True)
class MembershipContext:
    user: User
    member: CompanyMember

    @property
    def company_id(self) -> str:
        return self.member.company_id

    @property
    def role(self) -> Role:
        return Role(self.member.role)


READ_ROLES = {Role.owner, Role.manager, Role.accountant, Role.operator, Role.viewer}
MANAGE_TRANSACTION_ROLES = {Role.owner, Role.manager, Role.accountant}
CREATE_TRANSACTION_ROLES = {Role.owner, Role.manager, Role.accountant, Role.operator}
MANAGE_CATEGORY_ROLES = {Role.owner, Role.manager}
MANAGE_MEMBER_ROLES = {Role.owner, Role.manager}
APPROVE_ROLES = {Role.owner, Role.manager, Role.accountant}


def require_role(ctx: MembershipContext, allowed: set[Role]) -> None:
    if ctx.role not in allowed:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")


def can_delete_confirmed(ctx: MembershipContext) -> bool:
    return ctx.role in MANAGE_TRANSACTION_ROLES or (ctx.role == Role.operator and ctx.member.can_delete_confirmed)
