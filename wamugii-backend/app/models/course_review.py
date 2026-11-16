from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Integer, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class CourseReview(Base):
    """
    A student's star rating (1-5) and optional comment on a course.

    One per student per course: writing again updates the same row, so the
    average can't be inflated by one person. Only students with an ACTIVE
    enrollment who have done part of the course may review
    (see services/course_reviews.py). Staff can hide a review that breaks the
    rules; hidden reviews stay in the table but are left out of the public
    list and of the average.
    """

    __tablename__ = "course_reviews"
    __table_args__ = (
        UniqueConstraint("course_id", "user_id", name="uq_course_review_user"),
        CheckConstraint("rating BETWEEN 1 AND 5", name="ck_course_review_rating"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    rating: Mapped[int] = mapped_column(Integer)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_hidden: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user = relationship("User")
    course = relationship("Course")
