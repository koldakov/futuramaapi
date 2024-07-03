"""Add secret message model

Revision ID: 2693764b6723
Revises: 4d5b68e5d9df
Create Date: 2024-07-03 22:08:21.410931
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "2693764b6723"
down_revision: str | None = "4d5b68e5d9df"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "secret_messages",
        sa.Column(
            "text",
            sa.TEXT(),
            nullable=False,
        ),
        sa.Column(
            "visit_counter",
            sa.BIGINT(),
            nullable=False,
        ),
        sa.Column(
            "ip_address",
            sa.VARCHAR(length=64),
            nullable=False,
        ),
        sa.Column(
            "url",
            sa.VARCHAR(length=128),
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
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("url"),
        sa.UniqueConstraint("uuid"),
    )


def downgrade() -> None:
    op.drop_table("secret_messages")
