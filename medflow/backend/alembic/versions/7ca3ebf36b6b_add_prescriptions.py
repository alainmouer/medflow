"""add_prescriptions

Revision ID: 7ca3ebf36b6b
Revises: 9ddf50305e02
Create Date: 2026-06-08 09:01:12.144355

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7ca3ebf36b6b'
down_revision = '9ddf50305e02'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('prescriptions',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('tenant_id', sa.String(length=36), nullable=False),
    sa.Column('episode_id', sa.String(length=36), nullable=False),
    sa.Column('status', sa.String(length=50), nullable=False),
    sa.Column('medications', sa.Text(), nullable=True),
    sa.Column('dosage', sa.String(length=200), nullable=True),
    sa.Column('duration', sa.String(length=100), nullable=True),
    sa.Column('instructions', sa.Text(), nullable=True),
    sa.Column('warnings', sa.Text(), nullable=True),
    sa.Column('created_by', sa.String(length=36), nullable=True),
    sa.Column('signed_by', sa.String(length=36), nullable=True),
    sa.Column('signed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('prescriptions')
