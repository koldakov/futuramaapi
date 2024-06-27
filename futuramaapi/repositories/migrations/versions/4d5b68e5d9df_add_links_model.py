"""Add links model

Revision ID: 4d5b68e5d9df
Revises: ee5656c8dc7f
Create Date: 2024-06-25 22:36:03.747684

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "4d5b68e5d9df"
down_revision: str | None = "ee5656c8dc7f"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "links",
        sa.Column(
            "url",
            sa.VARCHAR(length=4096),
            nullable=False,
        ),
        sa.Column(
            "shortened",
            sa.VARCHAR(length=128),
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
            "counter",
            sa.BigInteger(),
            nullable=False,
            default=0,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("shortened"),
        sa.UniqueConstraint("uuid"),
    )


def downgrade() -> None:
    op.drop_table("links")
