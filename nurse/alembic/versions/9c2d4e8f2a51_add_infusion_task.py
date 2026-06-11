"""add infusion task

Revision ID: 9c2d4e8f2a51
Revises: 3a6f8bb0a9b1
Create Date: 2026-04-07 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9c2d4e8f2a51"
down_revision: Union[str, Sequence[str], None] = "3a6f8bb0a9b1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "infusion_task",
        sa.Column("task_id", sa.String(length=36), nullable=False),
        sa.Column("time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("target_id", sa.String(length=50), nullable=False),
        sa.Column("target_role", sa.String(length=20), nullable=False),
        sa.Column("fluids", sa.JSON(), nullable=False),
        sa.Column("current_fluid", sa.JSON(), nullable=True),
        sa.Column("is_completed", sa.Boolean(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("status_updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("task_id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("infusion_task")

