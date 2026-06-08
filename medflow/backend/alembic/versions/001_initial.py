"""Initial migration: tenants and users tables.

Revision ID: 001
Revises:
Create Date: 2026-06-07

"""
from __future__ import annotations

import uuid
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "001"
down_revision: str | None = None
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    # Tenants table
    op.create_table(
        "tenants",
        sa.Column("id", sa.String(36), primary_key=True, default=lambda: str(uuid.uuid4())),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("slug", sa.String(100), unique=True, nullable=False),
        sa.Column("specialty", sa.String(100), nullable=True),
        sa.Column("address", sa.Text, nullable=True),
        sa.Column("phone", sa.String(20), nullable=True),
        sa.Column("email", sa.String(100), nullable=True),
        sa.Column("is_active", sa.Boolean, default=True, nullable=False),
        sa.Column("plan", sa.String(50), default="internal", nullable=False),
        sa.Column("hds_certified", sa.Boolean, default=False, nullable=False),
        sa.Column("settings", sa.Text, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
    )

    # Users table
    op.create_table(
        "users",
        sa.Column("id", sa.String(36), primary_key=True, default=lambda: str(uuid.uuid4())),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("email", sa.String(100), unique=True, nullable=False),
        sa.Column("hashed_password", sa.String(200), nullable=False),
        sa.Column("full_name", sa.String(100), nullable=False),
        sa.Column("role", sa.String(50), nullable=False),
        sa.Column("specialty", sa.String(100), nullable=True),
        sa.Column("mfa_enabled", sa.Boolean, default=False, nullable=False),
        sa.Column("mfa_secret", sa.String(64), nullable=True),
        sa.Column("is_active", sa.Boolean, default=True, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
    )

    # Index for tenant_id on users (multi-tenant query performance)
    op.create_index("ix_users_tenant_id", "users", ["tenant_id"])


def downgrade() -> None:
    op.drop_index("ix_users_tenant_id", table_name="users")
    op.drop_table("users")
    op.drop_table("tenants")