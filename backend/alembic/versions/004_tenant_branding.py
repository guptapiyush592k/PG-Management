"""tenant branding and subscription fields

Revision ID: 004_tenant_branding
Revises: 003_refresh_tokens
Create Date: 2026-06-13

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "004_tenant_branding"
down_revision: Union[str, None] = "003_refresh_tokens"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("tenants", sa.Column("logo_url", sa.String(length=500), nullable=True))
    op.add_column(
        "tenants",
        sa.Column(
            "primary_color",
            sa.String(length=7),
            nullable=False,
            server_default="#2563EB",
        ),
    )
    op.add_column(
        "tenants",
        sa.Column(
            "secondary_color",
            sa.String(length=7),
            nullable=False,
            server_default="#1E40AF",
        ),
    )
    op.add_column(
        "tenants",
        sa.Column("is_demo", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )
    op.add_column(
        "tenants",
        sa.Column(
            "subscription_status",
            sa.Enum(
                "active",
                "trial",
                "expired",
                "cancelled",
                name="subscription_status",
                native_enum=False,
            ),
            nullable=False,
            server_default="trial",
        ),
    )
    op.execute(
        """
        UPDATE tenants
        SET is_demo = true, subscription_status = 'trial'
        WHERE slug = 'demo'
        """
    )
    op.alter_column("tenants", "primary_color", server_default=None)
    op.alter_column("tenants", "secondary_color", server_default=None)
    op.alter_column("tenants", "is_demo", server_default=None)
    op.alter_column("tenants", "subscription_status", server_default=None)


def downgrade() -> None:
    op.drop_column("tenants", "subscription_status")
    op.drop_column("tenants", "is_demo")
    op.drop_column("tenants", "secondary_color")
    op.drop_column("tenants", "primary_color")
    op.drop_column("tenants", "logo_url")
