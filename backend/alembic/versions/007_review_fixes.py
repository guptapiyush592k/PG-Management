"""Review fixes: booking constraint and refresh token index

Revision ID: 007_review_fixes
Revises: 006_stored_files
Create Date: 2026-06-20

"""

from typing import Sequence, Union

from alembic import op

revision: str = "007_review_fixes"
down_revision: Union[str, None] = "006_stored_files"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS uq_bookings_one_active_per_bed
        ON bookings (bed_id)
        WHERE status = 'active'
        """
    )
    op.create_index(
        "ix_refresh_tokens_expires_at",
        "refresh_tokens",
        ["expires_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_refresh_tokens_expires_at", table_name="refresh_tokens")
    op.execute("DROP INDEX IF EXISTS uq_bookings_one_active_per_bed")
