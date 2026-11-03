"""
Daily "continue your course" reminder sweep.

Emails every student who has an ACTIVE, unfinished enrollment and hasn't
completed a lesson for INACTIVE_DAYS days -- at most once every REMIND_EVERY_DAYS
per enrollment (tracked in `enrollments.last_reminder_at`).

Run once a day from cron on the droplet:

    docker exec wamugii-backend python -m app.send_course_reminders

`--dry-run` lists who would be emailed without sending anything.
"""

import sys
from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.core.database import SessionLocal
from app.crud import course as course_crud
from app.models.course import Enrollment, EnrollmentStatus
from app.services import notifications

INACTIVE_DAYS = 3
REMIND_EVERY_DAYS = 7


def _aware(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def main(dry_run: bool = False) -> int:
    now = datetime.now(timezone.utc)
    sent = 0
    db = SessionLocal()
    try:
        enrollments = db.scalars(
            select(Enrollment).where(
                Enrollment.is_active.is_(True),
                Enrollment.status == EnrollmentStatus.ACTIVE,
                Enrollment.completed_at.is_(None),
            )
        ).all()
        for enrollment in enrollments:
            course = course_crud.get_course(db, enrollment.course_id)
            if course is None or not course.is_active:
                continue
            total = course_crud.count_active_lessons(db, course.id)
            completed = course_crud.count_completed_lessons(db, enrollment.id)
            percent = course_crud.progress_percent(completed, total)
            if total == 0 or percent >= 100:
                continue

            last_activity = _aware(course_crud.last_activity_at(db, enrollment))
            if last_activity and now - last_activity < timedelta(days=INACTIVE_DAYS):
                continue
            last_reminder = _aware(enrollment.last_reminder_at)
            if last_reminder and now - last_reminder < timedelta(days=REMIND_EVERY_DAYS):
                continue

            nxt = course_crud.next_lesson(db, course.id, enrollment.id)
            if dry_run:
                print(f"would remind enrollment {enrollment.id} ({course.title}, {percent}%)")
                continue
            if notifications.send_course_reminder(db, enrollment, course, nxt.title if nxt else None, percent):
                enrollment.last_reminder_at = now
                db.commit()
                sent += 1
    finally:
        db.close()
    print(f"course reminders sent: {sent}")
    return sent


if __name__ == "__main__":
    main(dry_run="--dry-run" in sys.argv)
