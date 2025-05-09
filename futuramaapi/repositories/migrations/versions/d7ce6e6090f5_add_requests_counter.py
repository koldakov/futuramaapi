"""Add requests counter

Revision ID: d7ce6e6090f5
Revises: 81f374066bbf
Create Date: 2025-05-09 19:51:59.241837

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "d7ce6e6090f5"
down_revision: str | None = "81f374066bbf"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "requests_counter",
        sa.Column(
            "url",
            sa.VARCHAR(length=64),
            nullable=False,
        ),
        sa.Column(
            "counter",
            sa.BIGINT(),
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
    op.drop_table("requests_counter")
