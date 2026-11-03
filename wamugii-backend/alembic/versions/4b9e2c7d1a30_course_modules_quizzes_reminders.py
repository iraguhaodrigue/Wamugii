"""course modules, lesson durations, quizzes and reminder tracking

Revision ID: 4b9e2c7d1a30
Revises: 28f8dad700a1
Create Date: 2026-11-03 10:30:00

* lessons.module_title / lessons.duration_minutes -- group lessons into weeks
  and show study time.
* enrollments.last_reminder_at / enrollments.completed_at -- the weekly
  "continue your course" reminder and the one-time certificate email.
* lesson_quiz_questions / lesson_quiz_attempts -- auto-marked lesson quizzes.
* notificationtype gains COURSE_COMPLETED (dialect-guarded ALTER TYPE, same
  pattern as every earlier enum-extending migration).
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '4b9e2c7d1a30'
down_revision: Union[str, None] = '28f8dad700a1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _extend_notification_enum() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return
    op.execute("COMMIT")
    op.execute("ALTER TYPE notificationtype ADD VALUE IF NOT EXISTS 'COURSE_COMPLETED'")


def upgrade() -> None:
    with op.batch_alter_table('lessons') as batch:
        batch.add_column(sa.Column('module_title', sa.String(length=255), nullable=True))
        batch.add_column(sa.Column('duration_minutes', sa.Integer(), nullable=True))

    with op.batch_alter_table('enrollments') as batch:
        batch.add_column(sa.Column('last_reminder_at', sa.DateTime(timezone=True), nullable=True))
        batch.add_column(sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True))

    op.create_table(
        'lesson_quiz_questions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('lesson_id', sa.Integer(), nullable=False),
        sa.Column('question', sa.Text(), nullable=False),
        sa.Column('options', sa.JSON(), nullable=False),
        sa.Column('correct_index', sa.Integer(), nullable=False),
        sa.Column('explanation', sa.Text(), nullable=False),
        sa.Column('display_order', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['lesson_id'], ['lessons.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_lesson_quiz_questions_id'), 'lesson_quiz_questions', ['id'], unique=False)
    op.create_index(op.f('ix_lesson_quiz_questions_lesson_id'), 'lesson_quiz_questions', ['lesson_id'], unique=False)

    op.create_table(
        'lesson_quiz_attempts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('enrollment_id', sa.Integer(), nullable=False),
        sa.Column('lesson_id', sa.Integer(), nullable=False),
        sa.Column('score', sa.Integer(), nullable=False),
        sa.Column('total', sa.Integer(), nullable=False),
        sa.Column('passed', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['enrollment_id'], ['enrollments.id'], ),
        sa.ForeignKeyConstraint(['lesson_id'], ['lessons.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_lesson_quiz_attempts_id'), 'lesson_quiz_attempts', ['id'], unique=False)
    op.create_index(op.f('ix_lesson_quiz_attempts_enrollment_id'), 'lesson_quiz_attempts', ['enrollment_id'], unique=False)
    op.create_index(op.f('ix_lesson_quiz_attempts_lesson_id'), 'lesson_quiz_attempts', ['lesson_id'], unique=False)

    _extend_notification_enum()


def downgrade() -> None:
    op.drop_index(op.f('ix_lesson_quiz_attempts_lesson_id'), table_name='lesson_quiz_attempts')
    op.drop_index(op.f('ix_lesson_quiz_attempts_enrollment_id'), table_name='lesson_quiz_attempts')
    op.drop_index(op.f('ix_lesson_quiz_attempts_id'), table_name='lesson_quiz_attempts')
    op.drop_table('lesson_quiz_attempts')
    op.drop_index(op.f('ix_lesson_quiz_questions_lesson_id'), table_name='lesson_quiz_questions')
    op.drop_index(op.f('ix_lesson_quiz_questions_id'), table_name='lesson_quiz_questions')
    op.drop_table('lesson_quiz_questions')
    with op.batch_alter_table('enrollments') as batch:
        batch.drop_column('completed_at')
        batch.drop_column('last_reminder_at')
    with op.batch_alter_table('lessons') as batch:
        batch.drop_column('duration_minutes')
        batch.drop_column('module_title')
