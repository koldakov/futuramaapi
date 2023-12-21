"""Add broadcast number to episode

Revision ID: 1b86ee33d1ba
Revises: c03e060df1b8
Create Date: 2023-12-21 21:57:04.032458
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "1b86ee33d1ba"
down_revision: Union[str, None] = "c03e060df1b8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


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
