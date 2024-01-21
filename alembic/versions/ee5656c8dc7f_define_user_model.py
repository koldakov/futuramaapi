"""Define user model

Revision ID: ee5656c8dc7f
Revises: 1b86ee33d1ba
Create Date: 2024-01-21 21:40:59.557432
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "ee5656c8dc7f"
down_revision: Union[str, None] = "1b86ee33d1ba"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column(
            "name",
            sa.VARCHAR(length=64),
            nullable=False,
        ),
        sa.Column(
            "surname",
            sa.VARCHAR(length=64),
            nullable=False,
        ),
        sa.Column(
            "middle_name",
            sa.VARCHAR(length=64),
            nullable=True,
        ),
        sa.Column(
            "email",
            sa.VARCHAR(length=320),
            nullable=False,
        ),
        sa.Column(
            "username",
            sa.VARCHAR(length=64),
            nullable=False,
        ),
        sa.Column(
            "password",
            sa.VARCHAR(length=128),
            nullable=False,
        ),
        sa.Column(
            "is_confirmed",
            sa.Boolean(),
            nullable=True,
        ),
        sa.Column(
            "is_subscribed",
            sa.Boolean(),
            nullable=True,
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
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("username"),
        sa.UniqueConstraint("uuid"),
    )


def downgrade() -> None:
    op.drop_table("users")
