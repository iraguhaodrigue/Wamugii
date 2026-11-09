"""domain search log and DOMAIN_REQUESTED notifications

Revision ID: b7d2e4f6a8c1
Revises: 7c3d5e9a2b14
Create Date: 2026-11-09 12:30:00

Adds the `domain_searches` table (what people search for, shown on the admin
domain dashboard) and the DOMAIN_REQUESTED notification type (a client asked
for a domain from the search page).

It also adds the common second-level Rwandan extensions (.co.rw, .org.rw,
.ac.rw) to the price list as INACTIVE rows with placeholder costs: an admin
sets the real cost and switches them on from the dashboard. Existing rows are
never touched.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "b7d2e4f6a8c1"
down_revision: Union[str, None] = "7c3d5e9a2b14"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

NEW_NOTIFICATION_TYPES = ("DOMAIN_REQUESTED",)

# Placeholders, inactive until an admin enters the real registrar cost.
NEW_EXTENSIONS = [
    (".co.rw", "14000.00", "5000.00", 7),
    (".org.rw", "14000.00", "5000.00", 8),
    (".ac.rw", "14000.00", "5000.00", 9),
]


def _extend_notification_enum() -> None:
    """PostgreSQL needs ALTER TYPE for a new enum value; SQLite needs nothing."""
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return
    op.execute("COMMIT")
    for value in NEW_NOTIFICATION_TYPES:
        op.execute(f"ALTER TYPE notificationtype ADD VALUE IF NOT EXISTS '{value}'")


def upgrade() -> None:
    op.create_table(
        "domain_searches",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("query", sa.String(length=100), nullable=False),
        sa.Column("available_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("taken_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_domain_searches_id"), "domain_searches", ["id"], unique=False)
    op.create_index(op.f("ix_domain_searches_query"), "domain_searches", ["query"], unique=False)
    op.create_index(op.f("ix_domain_searches_user_id"), "domain_searches", ["user_id"], unique=False)
    op.create_index(op.f("ix_domain_searches_created_at"), "domain_searches", ["created_at"], unique=False)

    bind = op.get_bind()
    for extension, cost, margin, order in NEW_EXTENSIONS:
        if bind.dialect.name == "postgresql":
            sql = ("INSERT INTO domain_extensions (extension, cost_price, margin, is_active, display_order, "
                   "created_at, updated_at) VALUES (:e, :c, :m, false, :o, now(), now()) "
                   "ON CONFLICT (extension) DO NOTHING")
        else:
            sql = ("INSERT OR IGNORE INTO domain_extensions (extension, cost_price, margin, is_active, "
                   "display_order, created_at, updated_at) VALUES (:e, :c, :m, 0, :o, CURRENT_TIMESTAMP, "
                   "CURRENT_TIMESTAMP)")
        bind.execute(sa.text(sql), {"e": extension, "c": cost, "m": margin, "o": order})

    _extend_notification_enum()


def downgrade() -> None:
    op.drop_index(op.f("ix_domain_searches_created_at"), table_name="domain_searches")
    op.drop_index(op.f("ix_domain_searches_user_id"), table_name="domain_searches")
    op.drop_index(op.f("ix_domain_searches_query"), table_name="domain_searches")
    op.drop_index(op.f("ix_domain_searches_id"), table_name="domain_searches")
    op.drop_table("domain_searches")
    # Enum values cannot be removed from a PostgreSQL type; the extra value is harmless.
