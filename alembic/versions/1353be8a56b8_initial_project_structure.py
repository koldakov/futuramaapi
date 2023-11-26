"""Initial project structure

Revision ID: 1353be8a56b8
Revises: d413d1284339
Create Date: 2023-12-02 18:33:01.171361
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "1353be8a56b8"
down_revision: Union[str, None] = "d413d1284339"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "characters",
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "name",
            sa.VARCHAR(length=128),
            nullable=False,
        ),
        sa.Column(
            "status",
            postgresql.ENUM(
                "ALIVE",
                "DEAD",
                "UNKNOWN",
                name="characterstatus",
            ),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "gender",
            postgresql.ENUM(
                "MALE",
                "FEMALE",
                "UNKNOWN",
                name="charactergender",
            ),
            nullable=False,
        ),
        sa.Column(
            "species",
            postgresql.ENUM(
                "HUMAN",
                "ROBOT",
                "HEAD",
                "ALIEN",
                "MUTANT",
                "MONSTER",
                "UNKNOWN",
                name="characterspecies",
            ),
            nullable=False,
        ),
        sa.Column(
            "uuid",
            sa.UUID(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("uuid"),
    )
    op.create_table(
        "seasons",
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
        sa.UniqueConstraint("uuid"),
    )
    op.create_table(
        "episodes",
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "name",
            sa.VARCHAR(length=128),
            nullable=True,
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
            "air_date",
            sa.Date(),
            nullable=True,
        ),
        sa.Column(
            "duration",
            sa.Integer(),
            nullable=True,
        ),
        sa.Column(
            "season_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["season_id"],
            ["seasons.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("uuid"),
    )
    op.create_table(
        "episode_character_association",
        sa.Column(
            "episode_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "character_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["character_id"],
            ["characters.id"],
        ),
        sa.ForeignKeyConstraint(
            ["episode_id"],
            ["episodes.id"],
        ),
        sa.PrimaryKeyConstraint(
            "episode_id",
            "character_id",
        ),
    )


def downgrade() -> None:
    op.drop_table("episode_character_association")
    op.drop_table("episodes")
    op.drop_table("seasons")
    op.drop_table("characters")

    # Drop types
    sa.Enum(
        name="characterstatus",
    ).drop(
        op.get_bind(),
        checkfirst=False,
    )
    sa.Enum(
        name="charactergender",
    ).drop(
        op.get_bind(),
        checkfirst=False,
    )
    sa.Enum(
        name="characterspecies",
    ).drop(
        op.get_bind(),
        checkfirst=False,
    )
