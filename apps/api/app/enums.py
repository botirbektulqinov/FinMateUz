from enum import StrEnum


class Role(StrEnum):
    owner = "owner"
    manager = "manager"
    accountant = "accountant"
    operator = "operator"
    viewer = "viewer"


class TransactionType(StrEnum):
    income = "income"
    expense = "expense"


class TransactionSource(StrEnum):
    telegram = "telegram"
    dashboard = "dashboard"


class TransactionStatus(StrEnum):
    pending = "pending"
    confirmed = "confirmed"
    rejected = "rejected"
    deleted = "deleted"


class AuditAction(StrEnum):
    transaction_create = "transaction_create"
    transaction_update = "transaction_update"
    transaction_delete = "transaction_delete"
    transaction_approve = "transaction_approve"
    transaction_reject = "transaction_reject"
    category_create = "category_create"
    category_update = "category_update"
    category_delete = "category_delete"
    user_login = "user_login"
