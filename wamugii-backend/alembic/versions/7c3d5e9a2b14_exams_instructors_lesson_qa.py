"""final exams, course instructors, lesson Q&A and full-lecture videos

Revision ID: 7c3d5e9a2b14
Revises: 4b9e2c7d1a30
Create Date: 2026-11-03 15:30:00

* role gains INSTRUCTOR; notificationtype gains EXAM_PASSED, LESSON_QUESTION,
  LESSON_ANSWER, COURSE_ASSIGNED (dialect-guarded ALTER TYPE, same pattern as
  every earlier enum-extending migration).
* courses.exam_* -- final exam rules (60 questions, 90 min, 60%, 3 attempts,
  24 h between attempts, 3 screen-leaves before auto-submit).
* lessons.extra_videos -- "full lecture" videos under the main video.
* enrollments.exam_extra_attempts -- extra attempts granted by an instructor.
* course_instructors, exam_questions, exam_attempts, lesson_questions,
  lesson_answers -- new tables.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '7c3d5e9a2b14'
down_revision: Union[str, None] = '4b9e2c7d1a30'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


NEW_NOTIFICATION_TYPES = ("EXAM_PASSED", "LESSON_QUESTION", "LESSON_ANSWER", "COURSE_ASSIGNED")


def _extend_enum(type_name: str, values: Sequence[str]) -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return
    op.execute("COMMIT")
    for value in values:
        op.execute(f"ALTER TYPE {type_name} ADD VALUE IF NOT EXISTS '{value}'")


def _ts(name: str = 'created_at'):
    return sa.Column(name, sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False)


def upgrade() -> None:
    _extend_enum("role", ("INSTRUCTOR",))
    _extend_enum("notificationtype", NEW_NOTIFICATION_TYPES)

    with op.batch_alter_table('courses') as batch:
        batch.add_column(sa.Column('exam_question_count', sa.Integer(), nullable=False, server_default='60'))
        batch.add_column(sa.Column('exam_minutes', sa.Integer(), nullable=False, server_default='90'))
        batch.add_column(sa.Column('exam_pass_percent', sa.Integer(), nullable=False, server_default='60'))
        batch.add_column(sa.Column('exam_max_attempts', sa.Integer(), nullable=False, server_default='3'))
        batch.add_column(sa.Column('exam_cooldown_hours', sa.Integer(), nullable=False, server_default='24'))
        batch.add_column(sa.Column('exam_max_leaves', sa.Integer(), nullable=False, server_default='3'))

    with op.batch_alter_table('lessons') as batch:
        batch.add_column(sa.Column('extra_videos', sa.JSON(), nullable=True))

    with op.batch_alter_table('enrollments') as batch:
        batch.add_column(sa.Column('exam_extra_attempts', sa.Integer(), nullable=False, server_default='0'))

    op.create_table(
        'course_instructors',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('course_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        _ts(),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('course_id', 'user_id', name='uq_course_instructor'),
    )
    op.create_index(op.f('ix_course_instructors_id'), 'course_instructors', ['id'])
    op.create_index(op.f('ix_course_instructors_course_id'), 'course_instructors', ['course_id'])
    op.create_index(op.f('ix_course_instructors_user_id'), 'course_instructors', ['user_id'])

    op.create_table(
        'exam_questions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('course_id', sa.Integer(), nullable=False),
        sa.Column('kind', sa.Enum('SINGLE', 'MULTIPLE', 'TRUE_FALSE', 'FILL_BLANK', name='examquestionkind'), nullable=False),
        sa.Column('question', sa.Text(), nullable=False),
        sa.Column('options', sa.JSON(), nullable=False),
        sa.Column('correct', sa.JSON(), nullable=False),
        sa.Column('explanation', sa.Text(), nullable=False),
        sa.Column('topic', sa.String(length=255), nullable=True),
        sa.Column('display_order', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        _ts(),
        _ts('updated_at'),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_exam_questions_id'), 'exam_questions', ['id'])
    op.create_index(op.f('ix_exam_questions_course_id'), 'exam_questions', ['course_id'])
    op.create_index(op.f('ix_exam_questions_kind'), 'exam_questions', ['kind'])
    op.create_index(op.f('ix_exam_questions_is_active'), 'exam_questions', ['is_active'])

    op.create_table(
        'exam_attempts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('course_id', sa.Integer(), nullable=False),
        sa.Column('enrollment_id', sa.Integer(), nullable=False),
        sa.Column('client_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.Enum('IN_PROGRESS', 'SUBMITTED', name='examattemptstatus'), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deadline_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('submitted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('submit_reason', sa.String(length=30), nullable=True),
        sa.Column('question_ids', sa.JSON(), nullable=False),
        sa.Column('option_orders', sa.JSON(), nullable=False),
        sa.Column('answers', sa.JSON(), nullable=False),
        sa.Column('leave_count', sa.Integer(), nullable=False),
        sa.Column('events', sa.JSON(), nullable=False),
        sa.Column('score', sa.Integer(), nullable=True),
        sa.Column('total', sa.Integer(), nullable=False),
        sa.Column('percent', sa.Integer(), nullable=True),
        sa.Column('passed', sa.Boolean(), nullable=False),
        sa.Column('topic_scores', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id']),
        sa.ForeignKeyConstraint(['enrollment_id'], ['enrollments.id']),
        sa.ForeignKeyConstraint(['client_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    for col in ('id', 'course_id', 'enrollment_id', 'client_id', 'status'):
        op.create_index(op.f(f'ix_exam_attempts_{col}'), 'exam_attempts', [col])

    op.create_table(
        'lesson_questions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('course_id', sa.Integer(), nullable=False),
        sa.Column('lesson_id', sa.Integer(), nullable=False),
        sa.Column('author_id', sa.Integer(), nullable=False),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        _ts(),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id']),
        sa.ForeignKeyConstraint(['lesson_id'], ['lessons.id']),
        sa.ForeignKeyConstraint(['author_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    for col in ('id', 'course_id', 'lesson_id', 'author_id', 'is_active'):
        op.create_index(op.f(f'ix_lesson_questions_{col}'), 'lesson_questions', [col])

    op.create_table(
        'lesson_answers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('question_id', sa.Integer(), nullable=False),
        sa.Column('author_id', sa.Integer(), nullable=False),
        sa.Column('body', sa.Text(), nullable=False),
        _ts(),
        sa.ForeignKeyConstraint(['question_id'], ['lesson_questions.id']),
        sa.ForeignKeyConstraint(['author_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    for col in ('id', 'question_id', 'author_id'):
        op.create_index(op.f(f'ix_lesson_answers_{col}'), 'lesson_answers', [col])


def downgrade() -> None:
    op.drop_table('lesson_answers')
    op.drop_table('lesson_questions')
    op.drop_table('exam_attempts')
    op.drop_table('exam_questions')
    op.drop_table('course_instructors')
    with op.batch_alter_table('enrollments') as batch:
        batch.drop_column('exam_extra_attempts')
    with op.batch_alter_table('lessons') as batch:
        batch.drop_column('extra_videos')
    with op.batch_alter_table('courses') as batch:
        for col in ('exam_max_leaves', 'exam_cooldown_hours', 'exam_max_attempts',
                    'exam_pass_percent', 'exam_minutes', 'exam_question_count'):
            batch.drop_column(col)
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("DROP TYPE IF EXISTS examattemptstatus")
        op.execute("DROP TYPE IF EXISTS examquestionkind")
    # The INSTRUCTOR role and the notification labels stay: PostgreSQL cannot
    # drop enum values, and leaving them is harmless.
