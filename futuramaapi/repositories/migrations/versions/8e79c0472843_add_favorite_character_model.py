"""Add favorite character model

Revision ID: 8e79c0472843
Revises: ca664de1bf44
Create Date: 2026-01-01 22:42:59.969711

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "8e79c0472843"
down_revision: str | None = "ca664de1bf44"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "favorite_characters",
        sa.Column(
            "user_uuid",
            sa.UUID(),
            nullable=False,
        ),
        sa.Column(
            "character_uuid",
            sa.UUID(),
            nullable=False,
        ),
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(
                timezone=True,
            ),
            server_default=sa.text(
                "now()",
            ),
            nullable=False,
        ),
        sa.Column(
            "uuid",
            sa.UUID(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            [
                "character_uuid",
            ],
            [
                "characters.uuid",
            ],
        ),
        sa.ForeignKeyConstraint(
            [
                "user_uuid",
            ],
            [
                "users.uuid",
            ],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_uuid",
            "character_uuid",
            name="uniq_favorite_user_character",
        ),
        sa.UniqueConstraint("uuid"),
    )


def downgrade() -> None:
    op.drop_table("favorite_characters")
