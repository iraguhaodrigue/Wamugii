"""
Course star ratings and reviews, and the Student Handbook information shown on
course pages.

Rules:
* One review per student per course; writing again updates it.
* Only a student with an ACTIVE enrollment who has completed at least a
  quarter of the lessons (minimum one) can review, so ratings come from people
  who have really studied the course.
* Hidden reviews (moderated by staff) are excluded from the public list and
  from the average.
"""
from __future__ import annotations

import json
import math
from functools import lru_cache
from pathlib import Path

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.crud import course as course_crud
from app.models.course import Course, CourseInstructor, EnrollmentStatus
from app.models.course_review import CourseReview
from app.models.user import User
from app.schemas.course_review import (
    CourseReviewsPage,
    HandbookInfo,
    MyReviewStatus,
    RatingSummary,
    ReviewAdminRead,
    ReviewPublic,
    ReviewWrite,
)

REVIEW_SHARE = 0.25
CONTENT_ROOT = Path(__file__).resolve().parents[1] / "course_content"


def short_name(full_name: str | None) -> str:
    """'Aline Uwase Mukamana' -> 'Aline M.' -- enough to feel real, not enough to find someone."""
    parts = (full_name or "").split()
    if not parts:
        return "Student"
    if len(parts) == 1:
        return parts[0]
    return f"{parts[0]} {parts[-1][0].upper()}."


def _public(review: CourseReview) -> ReviewPublic:
    return ReviewPublic(
        id=review.id,
        rating=review.rating,
        comment=review.comment,
        reviewer_name=short_name(review.user.full_name if review.user else None),
        created_at=review.created_at,
        updated_at=review.updated_at,
    )


def summary(db: Session, course_id: int) -> RatingSummary:
    rows = db.execute(
        select(CourseReview.rating, func.count())
        .where(CourseReview.course_id == course_id, CourseReview.is_hidden.is_(False))
        .group_by(CourseReview.rating)
    ).all()
    dist = {str(star): 0 for star in range(5, 0, -1)}
    total = 0
    points = 0
    for rating, count in rows:
        dist[str(rating)] = count
        total += count
        points += rating * count
    return RatingSummary(average=round(points / total, 1) if total else None, count=total, distribution=dist)


def summaries(db: Session, course_ids: list[int]) -> dict[int, tuple[float | None, int]]:
    """Average and count per course, in one query, for catalogue cards."""
    if not course_ids:
        return {}
    rows = db.execute(
        select(CourseReview.course_id, func.avg(CourseReview.rating), func.count())
        .where(CourseReview.course_id.in_(course_ids), CourseReview.is_hidden.is_(False))
        .group_by(CourseReview.course_id)
    ).all()
    return {cid: (round(float(avg), 1), count) for cid, avg, count in rows}


def public_page(db: Session, course: Course, limit: int, offset: int) -> CourseReviewsPage:
    """Visible reviews that have a comment, newest first, plus the rating summary."""
    base = select(CourseReview).where(
        CourseReview.course_id == course.id,
        CourseReview.is_hidden.is_(False),
        CourseReview.comment.is_not(None),
    )
    total = db.scalar(select(func.count()).select_from(base.subquery())) or 0
    rows = db.scalars(base.order_by(CourseReview.updated_at.desc(), CourseReview.id.desc()).limit(limit).offset(offset)).all()
    return CourseReviewsPage(summary=summary(db, course.id), reviews=[_public(r) for r in rows], total_with_comments=total)


def _eligibility(db: Session, course: Course, user: User) -> tuple[bool, str | None, int, int]:
    total = course_crud.count_active_lessons(db, course.id)
    needed = max(1, math.ceil(total * REVIEW_SHARE))
    enrollment = course_crud.get_enrollment_for_client(db, course.id, user.id)
    if enrollment is None or not enrollment.is_active:
        return False, "Enroll in the course to rate it.", 0, needed
    if enrollment.status != EnrollmentStatus.ACTIVE:
        return False, "You can rate the course once your access is active.", 0, needed
    done = len(course_crud.completed_lesson_ids(db, enrollment.id))
    if done < needed:
        return False, f"Complete {needed} lessons to rate this course (you have completed {done}).", done, needed
    return True, None, done, needed


def my_status(db: Session, course: Course, user: User) -> MyReviewStatus:
    ok, reason, done, needed = _eligibility(db, course, user)
    review = db.scalar(select(CourseReview).where(CourseReview.course_id == course.id, CourseReview.user_id == user.id))
    return MyReviewStatus(
        review=_public(review) if review else None,
        can_review=ok,
        reason=reason,
        completed_lessons=done,
        lessons_needed=needed,
    )


def write(db: Session, course: Course, user: User, data: ReviewWrite) -> MyReviewStatus:
    ok, reason, _done, _needed = _eligibility(db, course, user)
    if not ok:
        raise HTTPException(status_code=403, detail=reason)
    review = db.scalar(select(CourseReview).where(CourseReview.course_id == course.id, CourseReview.user_id == user.id))
    if review is None:
        review = CourseReview(course_id=course.id, user_id=user.id, rating=data.rating, comment=data.comment)
        db.add(review)
    else:
        review.rating = data.rating
        review.comment = data.comment
    db.commit()
    db.refresh(review)
    return my_status(db, course, user)


def delete(db: Session, course: Course, user: User) -> None:
    review = db.scalar(select(CourseReview).where(CourseReview.course_id == course.id, CourseReview.user_id == user.id))
    if review is None:
        raise HTTPException(status_code=404, detail="You have not rated this course")
    db.delete(review)
    db.commit()


def admin_list(db: Session, course_id: int) -> list[ReviewAdminRead]:
    rows = db.scalars(
        select(CourseReview).where(CourseReview.course_id == course_id).order_by(CourseReview.updated_at.desc())
    ).all()
    return [
        ReviewAdminRead(
            **_public(r).model_dump(),
            user_id=r.user_id,
            reviewer_full_name=r.user.full_name if r.user else "",
            is_hidden=r.is_hidden,
        )
        for r in rows
    ]


def moderate(db: Session, course_id: int, review_id: int, hidden: bool) -> ReviewAdminRead:
    review = db.get(CourseReview, review_id)
    if review is None or review.course_id != course_id:
        raise HTTPException(status_code=404, detail="Review not found")
    review.is_hidden = hidden
    db.commit()
    db.refresh(review)
    return ReviewAdminRead(
        **_public(review).model_dump(),
        user_id=review.user_id,
        reviewer_full_name=review.user.full_name if review.user else "",
        is_hidden=review.is_hidden,
    )


def instructor_names(db: Session, course_id: int) -> list[str]:
    rows = db.scalars(
        select(User.full_name)
        .join(CourseInstructor, CourseInstructor.user_id == User.id)
        .where(CourseInstructor.course_id == course_id, User.is_active.is_(True))
        .order_by(CourseInstructor.id)
    ).all()
    return [name for name in rows if name]


@lru_cache(maxsize=64)
def _handbook_meta(slug: str, mtime: float) -> dict | None:  # mtime is part of the cache key
    path = CONTENT_ROOT / "handbooks" / slug / "handbook.json"
    try:
        return json.loads(path.read_text("utf-8"))
    except (OSError, ValueError):
        return None


def handbook_info(slug: str) -> HandbookInfo | None:
    """Pages and words of the course's Student Handbook, if one has been built."""
    meta_path = CONTENT_ROOT / "handbooks" / slug / "handbook.json"
    if not meta_path.is_file():
        return None
    meta = _handbook_meta(slug, meta_path.stat().st_mtime)
    if not meta:
        return None
    return HandbookInfo(
        pages=int(meta.get("pages", 0)),
        words=int(meta.get("words", 0)),
        chapters=int(meta.get("chapters", 0)),
        sample_available=sample_chapter_path(slug) is not None,
    )


def sample_chapter_path(slug: str) -> Path | None:
    """Chapter 1 of a course that has a handbook -- free to download as a sample."""
    if not (CONTENT_ROOT / "handbooks" / slug / "handbook.json").is_file():
        return None
    path = CONTENT_ROOT / "pdfs" / slug / "01.pdf"
    return path if path.is_file() else None
