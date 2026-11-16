"""course reviews: star ratings and comments from students

Revision ID: c4e8a1f2d6b9
Revises: b7d2e4f6a8c1
Create Date: 2026-11-16 12:00:00.000000
"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "c4e8a1f2d6b9"
down_revision: Union[str, None] = "b7d2e4f6a8c1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "course_reviews",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("course_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("is_hidden", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["course_id"], ["courses.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("course_id", "user_id", name="uq_course_review_user"),
        sa.CheckConstraint("rating BETWEEN 1 AND 5", name="ck_course_review_rating"),
    )
    op.create_index(op.f("ix_course_reviews_id"), "course_reviews", ["id"], unique=False)
    op.create_index(op.f("ix_course_reviews_course_id"), "course_reviews", ["course_id"], unique=False)
    op.create_index(op.f("ix_course_reviews_user_id"), "course_reviews", ["user_id"], unique=False)
    op.create_index(op.f("ix_course_reviews_is_hidden"), "course_reviews", ["is_hidden"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_course_reviews_is_hidden"), table_name="course_reviews")
    op.drop_index(op.f("ix_course_reviews_user_id"), table_name="course_reviews")
    op.drop_index(op.f("ix_course_reviews_course_id"), table_name="course_reviews")
    op.drop_index(op.f("ix_course_reviews_id"), table_name="course_reviews")
    op.drop_table("course_reviews")
