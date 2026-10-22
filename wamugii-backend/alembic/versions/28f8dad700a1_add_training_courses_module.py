"""add training courses module

Revision ID: 28f8dad700a1
Revises: 9eca91f097b7
Create Date: 2026-10-22 12:21:53.073583

Creates the five training tables (courses, lessons, lesson_materials,
enrollments, lesson_progress) and extends `notificationtype` with the two
new training events through the dialect-guarded ALTER TYPE pattern used by
every prior enum-extending migration (hosting, support, domains, team).

Autogenerate also proposed `alter_column` on `users.role` -- the same
enum-length false positive. SQLAlchemy 2.x defaults Enum to
create_constraint=False so on SQLite that column is a plain VARCHAR with no
CHECK and no enforced length, and the PostgreSQL side of `role` was already
handled by `a3f71c2d9b48`.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '28f8dad700a1'
down_revision: Union[str, None] = '9eca91f097b7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


NEW_NOTIFICATION_TYPES = ("COURSE_ENROLLED", "COURSE_ACCESS_ACTIVE")


def _extend_notification_enum() -> None:
    """
    Teach `notificationtype` about the two training events.

    Same shape as previous enum migrations: COMMIT first so the ALTER TYPE
    doesn't run inside a transaction block (pre-12 PostgreSQL rule), then
    ADD VALUE IF NOT EXISTS so re-running is a no-op. SQLite needs nothing.
    """
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return
    op.execute("COMMIT")
    for value in NEW_NOTIFICATION_TYPES:
        op.execute(f"ALTER TYPE notificationtype ADD VALUE IF NOT EXISTS '{value}'")


def upgrade() -> None:
    op.create_table(
        'courses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('slug', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('cover_image_url', sa.String(length=500), nullable=True),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('is_free', sa.Boolean(), nullable=False),
        sa.Column('price', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('status', sa.Enum('DRAFT', 'PUBLISHED', name='coursestatus'), nullable=False),
        sa.Column('display_order', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_courses_category'), 'courses', ['category'], unique=False)
    op.create_index(op.f('ix_courses_display_order'), 'courses', ['display_order'], unique=False)
    op.create_index(op.f('ix_courses_id'), 'courses', ['id'], unique=False)
    op.create_index(op.f('ix_courses_is_active'), 'courses', ['is_active'], unique=False)
    op.create_index(op.f('ix_courses_slug'), 'courses', ['slug'], unique=True)
    op.create_index(op.f('ix_courses_status'), 'courses', ['status'], unique=False)

    op.create_table(
        'lessons',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('course_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('video_url', sa.String(length=500), nullable=True),
        sa.Column('display_order', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_lessons_course_id'), 'lessons', ['course_id'], unique=False)
    op.create_index(op.f('ix_lessons_display_order'), 'lessons', ['display_order'], unique=False)
    op.create_index(op.f('ix_lessons_id'), 'lessons', ['id'], unique=False)
    op.create_index(op.f('ix_lessons_is_active'), 'lessons', ['is_active'], unique=False)

    op.create_table(
        'lesson_materials',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('lesson_id', sa.Integer(), nullable=False),
        sa.Column('uploaded_by', sa.Integer(), nullable=False),
        sa.Column('original_filename', sa.String(length=255), nullable=False),
        sa.Column('stored_filename', sa.String(length=255), nullable=False),
        sa.Column('storage_path', sa.String(length=500), nullable=False),
        sa.Column('content_type', sa.String(length=100), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['lesson_id'], ['lessons.id'], ),
        sa.ForeignKeyConstraint(['uploaded_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_lesson_materials_id'), 'lesson_materials', ['id'], unique=False)
    op.create_index(op.f('ix_lesson_materials_is_active'), 'lesson_materials', ['is_active'], unique=False)
    op.create_index(op.f('ix_lesson_materials_lesson_id'), 'lesson_materials', ['lesson_id'], unique=False)
    op.create_index(op.f('ix_lesson_materials_uploaded_by'), 'lesson_materials', ['uploaded_by'], unique=False)

    op.create_table(
        'enrollments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('course_id', sa.Integer(), nullable=False),
        sa.Column('client_id', sa.Integer(), nullable=False),
        sa.Column('invoice_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.Enum('PENDING_PAYMENT', 'ACTIVE', 'CANCELLED', name='enrollmentstatus'), nullable=False),
        sa.Column('enrolled_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['client_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ),
        sa.ForeignKeyConstraint(['invoice_id'], ['invoices.id'], ),
        sa.PrimaryKeyConstraint('id'),
        # One enrollment per client per course: the enroll endpoint turns the
        # IntegrityError into a 409 / returns the existing row.
        sa.UniqueConstraint('course_id', 'client_id', name='uq_enrollments_course_client'),
    )
    op.create_index(op.f('ix_enrollments_client_id'), 'enrollments', ['client_id'], unique=False)
    op.create_index(op.f('ix_enrollments_course_id'), 'enrollments', ['course_id'], unique=False)
    op.create_index(op.f('ix_enrollments_id'), 'enrollments', ['id'], unique=False)
    op.create_index(op.f('ix_enrollments_invoice_id'), 'enrollments', ['invoice_id'], unique=False)
    op.create_index(op.f('ix_enrollments_is_active'), 'enrollments', ['is_active'], unique=False)
    op.create_index(op.f('ix_enrollments_status'), 'enrollments', ['status'], unique=False)

    op.create_table(
        'lesson_progress',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('enrollment_id', sa.Integer(), nullable=False),
        sa.Column('lesson_id', sa.Integer(), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['enrollment_id'], ['enrollments.id'], ),
        sa.ForeignKeyConstraint(['lesson_id'], ['lessons.id'], ),
        sa.PrimaryKeyConstraint('id'),
        # One completion row per (enrollment, lesson). `mark_lesson_complete`
        # upserts via a scalar() check so the IntegrityError path only trips
        # on a concurrent double-click, which it then no-ops.
        sa.UniqueConstraint('enrollment_id', 'lesson_id', name='uq_lesson_progress'),
    )
    op.create_index(op.f('ix_lesson_progress_enrollment_id'), 'lesson_progress', ['enrollment_id'], unique=False)
    op.create_index(op.f('ix_lesson_progress_id'), 'lesson_progress', ['id'], unique=False)
    op.create_index(op.f('ix_lesson_progress_lesson_id'), 'lesson_progress', ['lesson_id'], unique=False)

    _extend_notification_enum()


def downgrade() -> None:
    op.drop_index(op.f('ix_lesson_progress_lesson_id'), table_name='lesson_progress')
    op.drop_index(op.f('ix_lesson_progress_id'), table_name='lesson_progress')
    op.drop_index(op.f('ix_lesson_progress_enrollment_id'), table_name='lesson_progress')
    op.drop_table('lesson_progress')

    op.drop_index(op.f('ix_enrollments_status'), table_name='enrollments')
    op.drop_index(op.f('ix_enrollments_is_active'), table_name='enrollments')
    op.drop_index(op.f('ix_enrollments_invoice_id'), table_name='enrollments')
    op.drop_index(op.f('ix_enrollments_id'), table_name='enrollments')
    op.drop_index(op.f('ix_enrollments_course_id'), table_name='enrollments')
    op.drop_index(op.f('ix_enrollments_client_id'), table_name='enrollments')
    op.drop_table('enrollments')

    op.drop_index(op.f('ix_lesson_materials_uploaded_by'), table_name='lesson_materials')
    op.drop_index(op.f('ix_lesson_materials_lesson_id'), table_name='lesson_materials')
    op.drop_index(op.f('ix_lesson_materials_is_active'), table_name='lesson_materials')
    op.drop_index(op.f('ix_lesson_materials_id'), table_name='lesson_materials')
    op.drop_table('lesson_materials')

    op.drop_index(op.f('ix_lessons_is_active'), table_name='lessons')
    op.drop_index(op.f('ix_lessons_id'), table_name='lessons')
    op.drop_index(op.f('ix_lessons_display_order'), table_name='lessons')
    op.drop_index(op.f('ix_lessons_course_id'), table_name='lessons')
    op.drop_table('lessons')

    op.drop_index(op.f('ix_courses_status'), table_name='courses')
    op.drop_index(op.f('ix_courses_slug'), table_name='courses')
    op.drop_index(op.f('ix_courses_is_active'), table_name='courses')
    op.drop_index(op.f('ix_courses_id'), table_name='courses')
    op.drop_index(op.f('ix_courses_display_order'), table_name='courses')
    op.drop_index(op.f('ix_courses_category'), table_name='courses')
    op.drop_table('courses')

    # PostgreSQL only: the enum types owned by the dropped columns go with them.
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("DROP TYPE IF EXISTS coursestatus")
        op.execute("DROP TYPE IF EXISTS enrollmentstatus")

    # The two NotificationType values stay. Removing a PG ENUM label means
    # rebuilding the type and rewriting every dependent column, and unused
    # labels are harmless -- same call every prior migration made.
