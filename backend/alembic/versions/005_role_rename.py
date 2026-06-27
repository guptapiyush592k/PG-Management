"""rename staff role to manager and add super_admin

Revision ID: 005_role_rename
Revises: 004_tenant_branding
Create Date: 2026-06-20

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "005_role_rename"
down_revision: Union[str, None] = "004_tenant_branding"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_OLD_ROLE = sa.Enum("owner", "staff", name="tenant_user_role", native_enum=False)
_NEW_ROLE = sa.Enum(
    "owner",
    "staff",
    "manager",
    "super_admin",
    name="tenant_user_role",
    native_enum=False,
)


def upgrade() -> None:
    # Widen VARCHAR(5) → VARCHAR(11) before renaming staff → manager (7 chars).
    op.alter_column(
        "tenant_users",
        "role",
        existing_type=_OLD_ROLE,
        type_=_NEW_ROLE,
        existing_nullable=False,
    )
    op.execute("UPDATE tenant_users SET role = 'manager' WHERE role = 'staff'")


def downgrade() -> None:
    op.execute(
        "UPDATE tenant_users SET role = 'staff' WHERE role = 'manager'"
    )
    op.execute(
        "UPDATE tenant_users SET role = 'owner' WHERE role = 'super_admin'"
    )
    op.alter_column(
        "tenant_users",
        "role",
        existing_type=_NEW_ROLE,
        type_=_OLD_ROLE,
        existing_nullable=False,
    )
