"""add overdue status

Revision ID: c940f939f97d
Revises: effdceef9c8a
Create Date: 2026-08-13 12:29:10.998778

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c940f939f97d'
down_revision: Union[str, Sequence[str], None] = 'effdceef9c8a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("ALTER TYPE status ADD VALUE 'overdue'")


def downgrade() -> None:
    """Downgrade schema."""
    pass
