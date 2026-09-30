"""create hosting_plans and hosting_accounts, seed plans

Revision ID: 0f8a5b695eeb
Revises: 8565c92831ed
Create Date: 2026-09-30 12:18:37.595310
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '0f8a5b695eeb'
down_revision: Union[str, None] = '8565c92831ed'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# The two values added to NotificationType by the hosting module.
NEW_NOTIFICATION_TYPES = ("HOSTING_ACCOUNT_CREATED", "HOSTING_STATUS_CHANGED")

# Seeded on first run only — see _seed_plans.
SEED_PLANS = [
    {
        "name": "Starter",
        "features": "1 website, SSL, 25GB SSD, 1TB bandwidth",
        "monthly_price": "10000.00",
        "yearly_price": "100000.00",
        "display_order": 1,
    },
    {
        "name": "Business",
        "features": "3 websites, SSL, 50GB SSD, 2TB bandwidth, email support",
        "monthly_price": "20000.00",
        "yearly_price": "200000.00",
        "display_order": 2,
    },
    {
        "name": "Professional",
        "features": "5 websites, SSL, 60GB SSD, 3TB bandwidth, priority support",
        "monthly_price": "30000.00",
        "yearly_price": "300000.00",
        "display_order": 3,
    },
    {
        "name": "Enterprise",
        "features": "Unlimited websites, NVMe 70GB, 2TB bandwidth, dedicated support",
        "monthly_price": "50000.00",
        "yearly_price": "500000.00",
        "display_order": 4,
    },
]


def _extend_notification_enum() -> None:
    """
    Teach the notification type column about the two hosting events.

    PostgreSQL backs sa.Enum with a native ENUM type, so new values need an
    explicit ALTER TYPE. The COMMIT first is the standard workaround: on
    PostgreSQL before 12 an ADD VALUE cannot run inside a transaction block.

    SQLite needs nothing at all. SQLAlchemy 2.x defaults Enum to
    create_constraint=False, so the column is a plain VARCHAR with no CHECK,
    and SQLite does not enforce VARCHAR length — the longer value stores as-is.
    Autogenerate proposed an alter_column here purely because the declared
    length grew; running it would mean a pointless batch table rebuild.
    """
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return
    op.execute("COMMIT")
    for value in NEW_NOTIFICATION_TYPES:
        op.execute(f"ALTER TYPE notificationtype ADD VALUE IF NOT EXISTS '{value}'")


def _seed_plans() -> None:
    """Insert the four standard plans, but only into an empty table."""
    bind = op.get_bind()
    existing = bind.execute(sa.text("SELECT COUNT(*) FROM hosting_plans")).scalar() or 0
    if existing:
        return

    plans_table = sa.table(
        "hosting_plans",
        sa.column("name", sa.String),
        sa.column("features", sa.Text),
        sa.column("monthly_price", sa.Numeric),
        sa.column("yearly_price", sa.Numeric),
        sa.column("display_order", sa.Integer),
        sa.column("is_active", sa.Boolean),
    )
    op.bulk_insert(plans_table, [{**plan, "is_active": True} for plan in SEED_PLANS])


def upgrade() -> None:
    op.create_table('hosting_plans',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('features', sa.Text(), nullable=False),
    sa.Column('monthly_price', sa.Numeric(precision=12, scale=2), nullable=False),
    sa.Column('yearly_price', sa.Numeric(precision=12, scale=2), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('display_order', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_hosting_plans_display_order'), 'hosting_plans', ['display_order'], unique=False)
    op.create_index(op.f('ix_hosting_plans_id'), 'hosting_plans', ['id'], unique=False)
    op.create_index(op.f('ix_hosting_plans_is_active'), 'hosting_plans', ['is_active'], unique=False)
    op.create_table('hosting_accounts',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('client_id', sa.Integer(), nullable=False),
    sa.Column('plan_id', sa.Integer(), nullable=False),
    sa.Column('domain', sa.String(length=255), nullable=True),
    sa.Column('nameservers', sa.Text(), nullable=True),
    sa.Column('server_notes', sa.Text(), nullable=True),
    sa.Column('status', sa.Enum('PENDING', 'ACTIVE', 'SUSPENDED', 'EXPIRED', 'CANCELLED', name='hostingstatus'), nullable=False),
    sa.Column('billing_cycle', sa.Enum('MONTHLY', 'YEARLY', name='billingcycle'), nullable=False),
    sa.Column('start_date', sa.Date(), nullable=True),
    sa.Column('next_billing_date', sa.Date(), nullable=True),
    sa.Column('expires_at', sa.Date(), nullable=True),
    sa.Column('invoice_id', sa.Integer(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.ForeignKeyConstraint(['client_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['invoice_id'], ['invoices.id'], ),
    sa.ForeignKeyConstraint(['plan_id'], ['hosting_plans.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_hosting_accounts_client_id'), 'hosting_accounts', ['client_id'], unique=False)
    op.create_index(op.f('ix_hosting_accounts_domain'), 'hosting_accounts', ['domain'], unique=False)
    op.create_index(op.f('ix_hosting_accounts_expires_at'), 'hosting_accounts', ['expires_at'], unique=False)
    op.create_index(op.f('ix_hosting_accounts_id'), 'hosting_accounts', ['id'], unique=False)
    op.create_index(op.f('ix_hosting_accounts_invoice_id'), 'hosting_accounts', ['invoice_id'], unique=False)
    op.create_index(op.f('ix_hosting_accounts_plan_id'), 'hosting_accounts', ['plan_id'], unique=False)
    op.create_index(op.f('ix_hosting_accounts_status'), 'hosting_accounts', ['status'], unique=False)

    _seed_plans()
    _extend_notification_enum()


def downgrade() -> None:
    op.drop_index(op.f('ix_hosting_accounts_status'), table_name='hosting_accounts')
    op.drop_index(op.f('ix_hosting_accounts_plan_id'), table_name='hosting_accounts')
    op.drop_index(op.f('ix_hosting_accounts_invoice_id'), table_name='hosting_accounts')
    op.drop_index(op.f('ix_hosting_accounts_id'), table_name='hosting_accounts')
    op.drop_index(op.f('ix_hosting_accounts_expires_at'), table_name='hosting_accounts')
    op.drop_index(op.f('ix_hosting_accounts_domain'), table_name='hosting_accounts')
    op.drop_index(op.f('ix_hosting_accounts_client_id'), table_name='hosting_accounts')
    op.drop_table('hosting_accounts')
    op.drop_index(op.f('ix_hosting_plans_is_active'), table_name='hosting_plans')
    op.drop_index(op.f('ix_hosting_plans_id'), table_name='hosting_plans')
    op.drop_index(op.f('ix_hosting_plans_display_order'), table_name='hosting_plans')
    op.drop_table('hosting_plans')

    # The two NotificationType values are deliberately left in place. Removing a
    # value from a PostgreSQL ENUM means rebuilding the type and rewriting every
    # dependent column — far riskier than leaving two unused labels behind, and
    # they are harmless once nothing emits them.
