"""add domain extensions price list

Revision ID: 9eca91f097b7
Revises: 94f876a57b26
Create Date: 2026-10-08 12:08:54.339227

Autogenerate also proposed `alter_column` on `notifications.type` and
`users.role`. Both were dropped: they are the same enum-length false positive
every module that touched an enum has produced. SQLAlchemy 2.x defaults Enum
to create_constraint=False, so on SQLite those columns are plain VARCHARs with
no CHECK and no enforced length; the PostgreSQL side of both enums was
handled by the migrations that introduced the values (`ee1b297dd2fc` and
`a3f71c2d9b48`), so re-stating them here would be wrong as well as redundant.

The seed rows are inserted here, inside the same migration that creates the
table, so a fresh deploy has the price list ready. They are placeholder costs
-- an admin edits them against the real registrar invoices. The INSERT uses
`ON CONFLICT DO NOTHING` on PostgreSQL and `INSERT OR IGNORE` on SQLite, so
re-running (or applying this on a DB where an admin has already added the
same extension) does not clobber what is there.
"""
from typing import Sequence, Union
from decimal import Decimal

from alembic import op
import sqlalchemy as sa


revision: str = '9eca91f097b7'
down_revision: Union[str, None] = '94f876a57b26'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Placeholders -- these are not the real registrar costs. An admin edits them
# against the actual invoices once the module is live. Flat RWF 5,000 margin
# as the brief specified.
SEED_ROWS = [
    (".com", "16000.00", "5000.00", 1),
    (".rw",  "14000.00", "5000.00", 2),
    (".org", "17000.00", "5000.00", 3),
    (".net", "18000.00", "5000.00", 4),
    (".io",  "60000.00", "5000.00", 5),
    (".co",  "35000.00", "5000.00", 6),
]


def upgrade() -> None:
    op.create_table(
        'domain_extensions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('extension', sa.String(length=16), nullable=False),
        sa.Column('cost_price', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('margin', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('display_order', sa.Integer(), nullable=False),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('(CURRENT_TIMESTAMP)'),
            nullable=False,
        ),
        sa.Column(
            'updated_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('(CURRENT_TIMESTAMP)'),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        op.f('ix_domain_extensions_display_order'),
        'domain_extensions', ['display_order'], unique=False,
    )
    # Unique: there is one row per TLD, matched exactly on write.
    op.create_index(
        op.f('ix_domain_extensions_extension'),
        'domain_extensions', ['extension'], unique=True,
    )
    op.create_index(op.f('ix_domain_extensions_id'), 'domain_extensions', ['id'], unique=False)
    op.create_index(
        op.f('ix_domain_extensions_is_active'),
        'domain_extensions', ['is_active'], unique=False,
    )

    # Seed the starter rows idempotently. Dialect split because SQLite and
    # PostgreSQL spell the "insert if missing" clause differently.
    bind = op.get_bind()
    is_pg = bind.dialect.name == "postgresql"
    for extension, cost, margin, order in SEED_ROWS:
        if is_pg:
            bind.exec_driver_sql(
                """
                INSERT INTO domain_extensions
                    (extension, cost_price, margin, is_active, display_order,
                     created_at, updated_at)
                VALUES
                    (%s, %s, %s, true, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                ON CONFLICT (extension) DO NOTHING
                """,
                (extension, Decimal(cost), Decimal(margin), order),
            )
        else:
            bind.exec_driver_sql(
                """
                INSERT OR IGNORE INTO domain_extensions
                    (extension, cost_price, margin, is_active, display_order,
                     created_at, updated_at)
                VALUES
                    (?, ?, ?, 1, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """,
                (extension, cost, margin, order),
            )


def downgrade() -> None:
    op.drop_index(op.f('ix_domain_extensions_is_active'), table_name='domain_extensions')
    op.drop_index(op.f('ix_domain_extensions_id'), table_name='domain_extensions')
    op.drop_index(op.f('ix_domain_extensions_extension'), table_name='domain_extensions')
    op.drop_index(op.f('ix_domain_extensions_display_order'), table_name='domain_extensions')
    op.drop_table('domain_extensions')
