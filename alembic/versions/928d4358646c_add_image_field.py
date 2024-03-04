"""Add image field

Revision ID: 928d4358646c
Revises: 1353be8a56b8
Create Date: 2023-12-08 20:58:59.382849
"""
from collections.abc import Sequence

import sqlalchemy as sa
from fastapi_storages import FileSystemStorage
from fastapi_storages.integrations.sqlalchemy import ImageType

from alembic import op
from app.core import settings

# revision identifiers, used by Alembic.
revision: str = "928d4358646c"
down_revision: str | None = "1353be8a56b8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "characters",
        sa.Column(
            "image",
            ImageType(
                storage=FileSystemStorage(
                    path=settings.project_root / settings.static,
                ),
            ),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column(
        "characters",
        "image",
    )
