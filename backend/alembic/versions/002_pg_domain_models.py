"""pg domain models and tenant_users refactor

Revision ID: 002_pg_domain_models
Revises: 001_initial_tenant_user
Create Date: 2026-06-13

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "002_pg_domain_models"
down_revision: Union[str, None] = "001_initial_tenant_user"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "tenant_users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "role",
            sa.Enum("owner", "staff", name="tenant_user_role", native_enum=False),
            nullable=False,
            server_default="owner",
        ),
        sa.Column("is_primary", sa.Boolean(), nullable=False, server_default=sa.text("false")),
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
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "user_id", name="uq_tenant_users_tenant_user"),
    )
    op.create_index(op.f("ix_tenant_users_tenant_id"), "tenant_users", ["tenant_id"], unique=False)
    op.create_index(op.f("ix_tenant_users_user_id"), "tenant_users", ["user_id"], unique=False)
    op.create_index(op.f("ix_tenant_users_role"), "tenant_users", ["role"], unique=False)

    op.execute(
        """
        INSERT INTO tenant_users (id, tenant_id, user_id, role, is_primary, created_at, updated_at)
        SELECT gen_random_uuid(), tenant_id, id, role, true, created_at, updated_at
        FROM users
        """
    )

    op.add_column("tenants", sa.Column("phone", sa.String(length=20), nullable=True))
    op.add_column("tenants", sa.Column("address", sa.Text(), nullable=True))

    op.add_column(
        "users",
        sa.Column("full_name", sa.String(length=255), nullable=False, server_default=""),
    )
    op.drop_constraint("uq_users_tenant_email", "users", type_="unique")
    op.drop_index("ix_users_tenant_id", table_name="users")
    op.drop_constraint("users_tenant_id_fkey", "users", type_="foreignkey")
    op.drop_column("users", "tenant_id")
    op.drop_column("users", "role")
    op.alter_column("users", "full_name", server_default=None)
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    op.create_table(
        "flats",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("address", sa.Text(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
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
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_flats_tenant_id"), "flats", ["tenant_id"], unique=False)
    op.create_index(op.f("ix_flats_name"), "flats", ["name"], unique=False)

    op.create_table(
        "residents",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("phone", sa.String(length=20), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("aadhaar", sa.String(length=12), nullable=True),
        sa.Column("joining_date", sa.Date(), nullable=False),
        sa.Column("deposit", sa.Numeric(precision=10, scale=2), nullable=False, server_default="0"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
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
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "phone", name="uq_residents_tenant_phone"),
    )
    op.create_index(op.f("ix_residents_tenant_id"), "residents", ["tenant_id"], unique=False)
    op.create_index(op.f("ix_residents_name"), "residents", ["name"], unique=False)
    op.create_index(op.f("ix_residents_aadhaar"), "residents", ["aadhaar"], unique=False)

    op.create_table(
        "rooms",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("flat_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("room_number", sa.String(length=50), nullable=False),
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
        sa.ForeignKeyConstraint(["flat_id"], ["flats.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("flat_id", "room_number", name="uq_rooms_flat_room_number"),
    )
    op.create_index(op.f("ix_rooms_tenant_id"), "rooms", ["tenant_id"], unique=False)
    op.create_index(op.f("ix_rooms_flat_id"), "rooms", ["flat_id"], unique=False)

    op.create_table(
        "beds",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("room_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("bed_label", sa.String(length=50), nullable=False),
        sa.Column("rent_amount", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column(
            "status",
            sa.Enum("vacant", "occupied", "maintenance", name="bed_status", native_enum=False),
            nullable=False,
            server_default="vacant",
        ),
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
        sa.ForeignKeyConstraint(["room_id"], ["rooms.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("room_id", "bed_label", name="uq_beds_room_bed_label"),
    )
    op.create_index(op.f("ix_beds_tenant_id"), "beds", ["tenant_id"], unique=False)
    op.create_index(op.f("ix_beds_room_id"), "beds", ["room_id"], unique=False)
    op.create_index(op.f("ix_beds_status"), "beds", ["status"], unique=False)

    op.create_table(
        "bookings",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("resident_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("bed_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column(
            "status",
            sa.Enum("active", "completed", "cancelled", name="booking_status", native_enum=False),
            nullable=False,
            server_default="active",
        ),
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
        sa.ForeignKeyConstraint(["bed_id"], ["beds.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["resident_id"], ["residents.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_bookings_tenant_id"), "bookings", ["tenant_id"], unique=False)
    op.create_index(op.f("ix_bookings_resident_id"), "bookings", ["resident_id"], unique=False)
    op.create_index(op.f("ix_bookings_bed_id"), "bookings", ["bed_id"], unique=False)
    op.create_index(op.f("ix_bookings_status"), "bookings", ["status"], unique=False)
    op.create_index("ix_bookings_tenant_status", "bookings", ["tenant_id", "status"], unique=False)
    op.create_index("ix_bookings_bed_status", "bookings", ["bed_id", "status"], unique=False)

    op.create_table(
        "rent_payments",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("resident_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("booking_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("amount", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=False),
        sa.Column("paid_date", sa.Date(), nullable=True),
        sa.Column(
            "status",
            sa.Enum("paid", "pending", "partial", "overdue", name="payment_status", native_enum=False),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("payment_mode", sa.String(length=50), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
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
        sa.ForeignKeyConstraint(["booking_id"], ["bookings.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["resident_id"], ["residents.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_rent_payments_tenant_id"), "rent_payments", ["tenant_id"], unique=False)
    op.create_index(op.f("ix_rent_payments_resident_id"), "rent_payments", ["resident_id"], unique=False)
    op.create_index(op.f("ix_rent_payments_booking_id"), "rent_payments", ["booking_id"], unique=False)
    op.create_index(op.f("ix_rent_payments_due_date"), "rent_payments", ["due_date"], unique=False)
    op.create_index(op.f("ix_rent_payments_status"), "rent_payments", ["status"], unique=False)
    op.create_index(
        "ix_rent_payments_tenant_due_date",
        "rent_payments",
        ["tenant_id", "due_date"],
        unique=False,
    )
    op.create_index(
        "ix_rent_payments_tenant_status",
        "rent_payments",
        ["tenant_id", "status"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_rent_payments_tenant_status", table_name="rent_payments")
    op.drop_index("ix_rent_payments_tenant_due_date", table_name="rent_payments")
    op.drop_index(op.f("ix_rent_payments_status"), table_name="rent_payments")
    op.drop_index(op.f("ix_rent_payments_due_date"), table_name="rent_payments")
    op.drop_index(op.f("ix_rent_payments_booking_id"), table_name="rent_payments")
    op.drop_index(op.f("ix_rent_payments_resident_id"), table_name="rent_payments")
    op.drop_index(op.f("ix_rent_payments_tenant_id"), table_name="rent_payments")
    op.drop_table("rent_payments")

    op.drop_index("ix_bookings_bed_status", table_name="bookings")
    op.drop_index("ix_bookings_tenant_status", table_name="bookings")
    op.drop_index(op.f("ix_bookings_status"), table_name="bookings")
    op.drop_index(op.f("ix_bookings_bed_id"), table_name="bookings")
    op.drop_index(op.f("ix_bookings_resident_id"), table_name="bookings")
    op.drop_index(op.f("ix_bookings_tenant_id"), table_name="bookings")
    op.drop_table("bookings")

    op.drop_index(op.f("ix_beds_status"), table_name="beds")
    op.drop_index(op.f("ix_beds_room_id"), table_name="beds")
    op.drop_index(op.f("ix_beds_tenant_id"), table_name="beds")
    op.drop_table("beds")

    op.drop_index(op.f("ix_rooms_flat_id"), table_name="rooms")
    op.drop_index(op.f("ix_rooms_tenant_id"), table_name="rooms")
    op.drop_table("rooms")

    op.drop_index(op.f("ix_residents_aadhaar"), table_name="residents")
    op.drop_index(op.f("ix_residents_name"), table_name="residents")
    op.drop_index(op.f("ix_residents_tenant_id"), table_name="residents")
    op.drop_table("residents")

    op.drop_index(op.f("ix_flats_name"), table_name="flats")
    op.drop_index(op.f("ix_flats_tenant_id"), table_name="flats")
    op.drop_table("flats")

    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.add_column(
        "users",
        sa.Column(
            "role",
            sa.Enum("owner", "staff", name="user_role", native_enum=False),
            nullable=False,
            server_default="owner",
        ),
    )
    op.add_column("users", sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.execute(
        """
        UPDATE users u
        SET tenant_id = tu.tenant_id, role = tu.role
        FROM tenant_users tu
        WHERE tu.user_id = u.id AND tu.is_primary = true
        """
    )
    op.alter_column("users", "tenant_id", nullable=False)
    op.create_foreign_key("users_tenant_id_fkey", "users", "tenants", ["tenant_id"], ["id"], ondelete="CASCADE")
    op.create_index(op.f("ix_users_tenant_id"), "users", ["tenant_id"], unique=False)
    op.create_unique_constraint("uq_users_tenant_email", "users", ["tenant_id", "email"])
    op.drop_column("users", "full_name")

    op.drop_column("tenants", "address")
    op.drop_column("tenants", "phone")

    op.drop_index(op.f("ix_tenant_users_role"), table_name="tenant_users")
    op.drop_index(op.f("ix_tenant_users_user_id"), table_name="tenant_users")
    op.drop_index(op.f("ix_tenant_users_tenant_id"), table_name="tenant_users")
    op.drop_table("tenant_users")
