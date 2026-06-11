"""init

Revision ID: 3a6f8bb0a9b1
Revises:
Create Date: 2026-04-05 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "3a6f8bb0a9b1"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "dispensing_task",
        sa.Column("task_id", sa.String(length=36), nullable=False),
        sa.Column("time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("user_id", sa.String(length=50), nullable=False),
        sa.Column("user_role", sa.String(length=20), nullable=False),
        sa.Column("medicines", sa.JSON(), nullable=False),
        sa.Column("is_completed", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("task_id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("dispensing_task")
