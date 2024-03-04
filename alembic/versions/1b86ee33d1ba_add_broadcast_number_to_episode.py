"""Add broadcast number to episode

Revision ID: 1b86ee33d1ba
Revises: c03e060df1b8
Create Date: 2023-12-21 21:57:04.032458
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "1b86ee33d1ba"
down_revision: str | None = "c03e060df1b8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "episodes",
        sa.Column(
            "broadcast_number",
            sa.SmallInteger(),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column(
        "episodes",
        "broadcast_number",
    )
