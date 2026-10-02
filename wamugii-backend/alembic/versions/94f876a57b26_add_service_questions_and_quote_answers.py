"""add service questions and quote answers

Revision ID: 94f876a57b26
Revises: a3f71c2d9b48
Create Date: 2026-10-02 10:14:13.876267

Autogenerate also proposed `alter_column` on `notifications.type` and
`users.role`. Both were dropped: they are the same false positive every module
that touched an enum has produced. SQLAlchemy 2.x defaults Enum to
create_constraint=False, so on SQLite those columns are plain VARCHARs with no
CHECK and no enforced length -- the only thing that changed is the *declared*
length as values were added, which needs no DDL. The PostgreSQL side of those
two enums was already handled by the migrations that introduced the values
(`ee1b297dd2fc` and `a3f71c2d9b48`), so re-stating them here would be wrong as
well as unnecessary.

`questiontype` is a brand-new enum, created by `create_table` on both backends,
so it needs no ALTER TYPE of its own.

The two `services` columns are nullable with no default or constraint, which
SQLite accepts through a plain ALTER TABLE ADD COLUMN -- no batch mode needed.
Existing rows land NULL, which both new fields treat as "not set", so every
service that predates this renders exactly as it did before.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '94f876a57b26'
down_revision: Union[str, None] = 'a3f71c2d9b48'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'service_questions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('service_id', sa.Integer(), nullable=False),
        sa.Column('question_text', sa.String(length=500), nullable=False),
        sa.Column(
            'question_type',
            sa.Enum(
                'TEXT', 'TEXTAREA', 'NUMBER', 'SELECT', 'MULTISELECT', 'YES_NO',
                name='questiontype',
            ),
            nullable=False,
        ),
        # JSON-encoded list of choices, as Text rather than a JSON column so the
        # same migration runs on SQLite and PostgreSQL.
        sa.Column('options', sa.Text(), nullable=True),
        sa.Column('is_required', sa.Boolean(), nullable=False),
        sa.Column('display_order', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
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
        sa.ForeignKeyConstraint(['service_id'], ['services.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_service_questions_display_order'), 'service_questions', ['display_order'], unique=False)
    op.create_index(op.f('ix_service_questions_id'), 'service_questions', ['id'], unique=False)
    op.create_index(op.f('ix_service_questions_is_active'), 'service_questions', ['is_active'], unique=False)
    op.create_index(op.f('ix_service_questions_question_type'), 'service_questions', ['question_type'], unique=False)
    op.create_index(op.f('ix_service_questions_service_id'), 'service_questions', ['service_id'], unique=False)

    op.create_table(
        'quote_answers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('quote_request_id', sa.Integer(), nullable=False),
        # Nullable: historic quotes predate questions, and a submission can
        # carry a captured detail with no configured question behind it.
        sa.Column('question_id', sa.Integer(), nullable=True),
        # The text as asked at submit time, so editing a question later never
        # rewrites what an archived quote says it answered.
        sa.Column('question_text', sa.String(length=500), nullable=False),
        sa.Column('answer', sa.Text(), nullable=False),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('(CURRENT_TIMESTAMP)'),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(['question_id'], ['service_questions.id'], ),
        sa.ForeignKeyConstraint(['quote_request_id'], ['quote_requests.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_quote_answers_id'), 'quote_answers', ['id'], unique=False)
    op.create_index(op.f('ix_quote_answers_question_id'), 'quote_answers', ['question_id'], unique=False)
    op.create_index(op.f('ix_quote_answers_quote_request_id'), 'quote_answers', ['quote_request_id'], unique=False)

    op.add_column('services', sa.Column('long_description', sa.Text(), nullable=True))
    op.add_column('services', sa.Column('features', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('services', 'features')
    op.drop_column('services', 'long_description')

    op.drop_index(op.f('ix_quote_answers_quote_request_id'), table_name='quote_answers')
    op.drop_index(op.f('ix_quote_answers_question_id'), table_name='quote_answers')
    op.drop_index(op.f('ix_quote_answers_id'), table_name='quote_answers')
    op.drop_table('quote_answers')

    op.drop_index(op.f('ix_service_questions_service_id'), table_name='service_questions')
    op.drop_index(op.f('ix_service_questions_question_type'), table_name='service_questions')
    op.drop_index(op.f('ix_service_questions_is_active'), table_name='service_questions')
    op.drop_index(op.f('ix_service_questions_id'), table_name='service_questions')
    op.drop_index(op.f('ix_service_questions_display_order'), table_name='service_questions')
    op.drop_table('service_questions')

    # PostgreSQL only: the enum type the dropped column owned goes with it.
    # On SQLite question_type was a plain VARCHAR, so this is a no-op.
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("DROP TYPE IF EXISTS questiontype")
