"""design transformation

Revision ID: 0003
Revises: 0002
Create Date: 2026-11-02 10:00:00

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0003"
down_revision: str | Sequence[str] | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("designs", sa.Column("transformation", sa.String(length=40), nullable=True))


def downgrade() -> None:
    op.drop_column("designs", "transformation")
