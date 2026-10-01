"""add team members: approval status and project_members

Revision ID: a3f71c2d9b48
Revises: ee1b297dd2fc
Create Date: 2026-10-01 09:12:04.117823
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a3f71c2d9b48'
down_revision: Union[str, None] = 'ee1b297dd2fc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# The three values the team-member module adds to NotificationType.
NEW_NOTIFICATION_TYPES = (
    "TEAM_MEMBER_REGISTERED",
    "TEAM_MEMBER_APPROVED",
    "PROJECT_ASSIGNMENT",
)


def _extend_enum(type_name: str, values: Sequence[str]) -> None:
    """
    Add values to a PostgreSQL native ENUM; no-op everywhere else.

    Same pattern as the hosting, support and domains migrations: PostgreSQL
    backs sa.Enum with a real ENUM type, so a new label needs ALTER TYPE, and
    the COMMIT first is the standard workaround because on PostgreSQL before 12
    an ADD VALUE cannot run inside a transaction block.

    SQLite needs nothing: SQLAlchemy 2.x defaults Enum to
    create_constraint=False, so these columns are plain VARCHARs with no CHECK
    constraint and no enforced length.
    """
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return
    op.execute("COMMIT")
    for value in values:
        op.execute(f"ALTER TYPE {type_name} ADD VALUE IF NOT EXISTS '{value}'")


def upgrade() -> None:
    # TEAM_MEMBER joins the existing role enum. On PostgreSQL the type is named
    # after the Python class, lowercased -- `role`.
    _extend_enum("role", ("TEAM_MEMBER",))
    _extend_enum("notificationtype", NEW_NOTIFICATION_TYPES)

    # Every existing ADMIN/STAFF/CLIENT must come out of this APPROVED, or the
    # approval gate in deps.get_current_active_user would lock the whole app
    # out. The server_default does that for existing rows as the column is
    # added; the explicit UPDATE afterwards covers the (PostgreSQL) case where
    # the column is added nullable first and makes the intent legible either
    # way.
    op.add_column(
        'users',
        sa.Column(
            'approval_status',
            sa.Enum('PENDING', 'APPROVED', 'REJECTED', name='approvalstatus'),
            nullable=False,
            server_default='APPROVED',
        ),
    )
    op.execute("UPDATE users SET approval_status = 'APPROVED' WHERE approval_status IS NULL")
    op.create_index(
        op.f('ix_users_approval_status'), 'users', ['approval_status'], unique=False
    )

    op.create_table(
        'project_members',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column(
            'project_role',
            sa.Enum(
                'TEAM_LEAD', 'PROGRAMMER', 'TESTER', 'RESEARCHER', 'DESIGNER',
                name='projectrole',
            ),
            nullable=False,
        ),
        sa.Column(
            'assigned_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('(CURRENT_TIMESTAMP)'),
            nullable=False,
        ),
        sa.Column('assigned_by', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['assigned_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        # One role per person per project. The soft delete works with this
        # rather than around it: a removed member keeps their row and is
        # reactivated on re-assignment -- see crud/project_member.py.
        sa.UniqueConstraint('project_id', 'user_id', name='uq_project_members_project_user'),
    )
    op.create_index(op.f('ix_project_members_id'), 'project_members', ['id'], unique=False)
    op.create_index(
        op.f('ix_project_members_project_id'), 'project_members', ['project_id'], unique=False
    )
    op.create_index(
        op.f('ix_project_members_user_id'), 'project_members', ['user_id'], unique=False
    )
    op.create_index(
        op.f('ix_project_members_project_role'), 'project_members', ['project_role'], unique=False
    )
    op.create_index(
        op.f('ix_project_members_assigned_by'), 'project_members', ['assigned_by'], unique=False
    )
    op.create_index(
        op.f('ix_project_members_is_active'), 'project_members', ['is_active'], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f('ix_project_members_is_active'), table_name='project_members')
    op.drop_index(op.f('ix_project_members_assigned_by'), table_name='project_members')
    op.drop_index(op.f('ix_project_members_project_role'), table_name='project_members')
    op.drop_index(op.f('ix_project_members_user_id'), table_name='project_members')
    op.drop_index(op.f('ix_project_members_project_id'), table_name='project_members')
    op.drop_index(op.f('ix_project_members_id'), table_name='project_members')
    op.drop_table('project_members')

    op.drop_index(op.f('ix_users_approval_status'), table_name='users')
    op.drop_column('users', 'approval_status')

    # PostgreSQL only: the enum type the dropped column owned goes with it.
    # `projectrole` is dropped the same way; on SQLite both are no-ops because
    # the columns were plain VARCHARs.
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("DROP TYPE IF EXISTS approvalstatus")
        op.execute("DROP TYPE IF EXISTS projectrole")

    # The TEAM_MEMBER role label and the three NotificationType values are
    # deliberately left in place: removing a value from a PostgreSQL ENUM means
    # rebuilding the type and rewriting every dependent column, and an unused
    # label is harmless. Same call the hosting/support/domains migrations made.
