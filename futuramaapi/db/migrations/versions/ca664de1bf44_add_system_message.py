"""Add system message

Revision ID: ca664de1bf44
Revises: d7ce6e6090f5
Create Date: 2025-05-09 22:02:13.243371

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "ca664de1bf44"
down_revision: str | None = "d7ce6e6090f5"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "system_messages",
        sa.Column(
            "message",
            sa.TEXT(),
            nullable=False,
        ),
        sa.Column(
            "author_name",
            sa.VARCHAR(length=64),
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
        sa.UniqueConstraint("author_name"),
        sa.UniqueConstraint("uuid"),
    )


def downgrade() -> None:
    op.drop_table("system_messages")
