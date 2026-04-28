"""use bigint for telegram user ids

Revision ID: 0002_telegram_user_id_bigint
Revises: 0001_initial_schema
Create Date: 2026-04-28 09:34:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision = "0002_telegram_user_id_bigint"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "telegram_accounts",
        "telegram_user_id",
        existing_type=sa.Integer(),
        type_=sa.BigInteger(),
        existing_nullable=False,
        postgresql_using="telegram_user_id::bigint",
    )


def downgrade() -> None:
    op.alter_column(
        "telegram_accounts",
        "telegram_user_id",
        existing_type=sa.BigInteger(),
        type_=sa.Integer(),
        existing_nullable=False,
        postgresql_using="telegram_user_id::integer",
    )
