"""rename staff role to manager and add super_admin

Revision ID: 005_role_rename
Revises: 004_tenant_branding
Create Date: 2026-06-20

"""

from typing import Sequence, Union

from alembic import op

revision: str = "005_role_rename"
down_revision: Union[str, None] = "004_tenant_branding"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("UPDATE tenant_users SET role = 'manager' WHERE role = 'staff'")


def downgrade() -> None:
    op.execute(
        "UPDATE tenant_users SET role = 'staff' WHERE role = 'manager'"
    )
    op.execute(
        "UPDATE tenant_users SET role = 'owner' WHERE role = 'super_admin'"
    )
