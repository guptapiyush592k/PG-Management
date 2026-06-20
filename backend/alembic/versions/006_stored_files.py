"""stored_files table

Revision ID: 006_stored_files
Revises: 005_role_rename
Create Date: 2026-06-20

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "006_stored_files"
down_revision: Union[str, None] = "005_role_rename"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "stored_files",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("content_type", sa.String(length=255), nullable=False),
        sa.Column("storage_key", sa.String(length=500), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=True),
        sa.Column(
            "status",
            sa.Enum("pending", "uploaded", name="file_status", native_enum=False),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("uploaded_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["uploaded_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("storage_key"),
    )
    op.create_index(
        op.f("ix_stored_files_tenant_id"),
        "stored_files",
        ["tenant_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_stored_files_status"),
        "stored_files",
        ["status"],
        unique=False,
    )
    op.create_index(
        op.f("ix_stored_files_uploaded_by_user_id"),
        "stored_files",
        ["uploaded_by_user_id"],
        unique=False,
    )
    op.create_index(
        "ix_stored_files_tenant_created_at",
        "stored_files",
        ["tenant_id", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_stored_files_tenant_status",
        "stored_files",
        ["tenant_id", "status"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_stored_files_tenant_status", table_name="stored_files")
    op.drop_index("ix_stored_files_tenant_created_at", table_name="stored_files")
    op.drop_index(op.f("ix_stored_files_uploaded_by_user_id"), table_name="stored_files")
    op.drop_index(op.f("ix_stored_files_status"), table_name="stored_files")
    op.drop_index(op.f("ix_stored_files_tenant_id"), table_name="stored_files")
    op.drop_table("stored_files")
