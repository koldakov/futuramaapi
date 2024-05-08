"""Initial revision

Revision ID: d413d1284339
Revises:
Create Date: 2023-11-25 19:46:49.496715
"""

from collections.abc import Sequence

revision: str = "d413d1284339"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
