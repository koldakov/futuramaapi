"""Add auth session

Revision ID: 81f374066bbf
Revises: 2693764b6723
Create Date: 2024-07-12 16:11:24.004642

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "81f374066bbf"
down_revision: str | None = "2693764b6723"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "auth_sessions",
        sa.Column(
            "key",
            sa.VARCHAR(length=32),
            nullable=False,
        ),
        sa.Column(
            "ip_address",
            sa.VARCHAR(length=64),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "uuid",
            sa.UUID(),
            nullable=False,
        ),
        sa.Column(
            "expired",
            sa.Boolean(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("key"),
        sa.UniqueConstraint("uuid"),
    )


def downgrade() -> None:
    op.drop_table("auth_sessions")
