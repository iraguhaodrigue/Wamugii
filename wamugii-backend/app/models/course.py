import enum
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    JSON,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class CourseStatus(str, enum.Enum):
    """Draft while being written; published to be publicly listed."""

    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"


class EnrollmentStatus(str, enum.Enum):
    """
    Paid courses land PENDING_PAYMENT until the linked invoice is paid; free
    courses enroll straight into ACTIVE. CANCELLED is an admin or client exit.
    """

    PENDING_PAYMENT = "PENDING_PAYMENT"
    ACTIVE = "ACTIVE"
    CANCELLED = "CANCELLED"


class Course(Base):
    """
    A training course a client can enroll in.

    `is_free` is the switch: True means instant ACTIVE on enroll with no
    invoice; False means an invoice is generated and the enrollment stays
    PENDING_PAYMENT until an admin marks the invoice paid (same manual model
    as hosting and domains).

    `price` is nullable because a free course doesn't need one, and nullable
    beats a stored zero -- a reader can't be confused into thinking "0.00"
    might become something else later.

    Only PUBLISHED + is_active courses are returned by the public catalog.
    """

    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255))
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    description: Mapped[str] = mapped_column(Text)
    cover_image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)

    is_free: Mapped[bool] = mapped_column(Boolean, default=True)
    price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)

    status: Mapped[CourseStatus] = mapped_column(
        Enum(CourseStatus), default=CourseStatus.DRAFT, index=True
    )
    display_order: Mapped[int] = mapped_column(Integer, default=0, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    lessons = relationship(
        "Lesson",
        back_populates="course",
        order_by="Lesson.display_order, Lesson.id",
        cascade="all, delete-orphan",
    )
    enrollments = relationship("Enrollment", back_populates="course")


class Lesson(Base):
    """
    One lesson in a course.

    `video_url` is a YouTube or Vimeo URL. Only the URL is stored; the
    frontend parses the video id and renders the official embed iframe
    rather than injecting the raw URL into the DOM.

    `content` is the lesson body (text / markdown-ish). PDF materials attach
    through `LessonMaterial` -- a separate table rather than reusing the
    project-file model, which is tightly bound to projects.
    """

    __tablename__ = "lessons"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"), index=True)
    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text, default="")
    video_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    # Groups lessons into weeks/modules ("Week 1 · Understanding AI"). Lessons
    # with the same value are shown together, in display_order; null means the
    # course isn't organised into modules.
    module_title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    # Expected study time (reading + video + activity), shown to students.
    duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)

    display_order: Mapped[int] = mapped_column(Integer, default=0, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    course = relationship("Course", back_populates="lessons")
    materials = relationship(
        "LessonMaterial",
        back_populates="lesson",
        order_by="LessonMaterial.id",
        cascade="all, delete-orphan",
    )
    quiz_questions = relationship(
        "LessonQuizQuestion",
        back_populates="lesson",
        order_by="LessonQuizQuestion.display_order, LessonQuizQuestion.id",
        cascade="all, delete-orphan",
    )


class LessonMaterial(Base):
    """
    A PDF/document attached to a lesson.

    Separate from ProjectFile on purpose: that model is scoped by project_id,
    its storage path is `projects/{project_id}/...` and its queries assume
    projects everywhere. A nullable `lesson_id` on it would mean two
    unrelated foreign keys on one row and complicate every existing project
    query. This table mirrors the useful fields and files land under
    `lessons/{lesson_id}/` through the same `storage.save_file` service.
    """

    __tablename__ = "lesson_materials"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lessons.id"), index=True)
    uploaded_by: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    original_filename: Mapped[str] = mapped_column(String(255))
    stored_filename: Mapped[str] = mapped_column(String(255))
    storage_path: Mapped[str] = mapped_column(String(500))
    content_type: Mapped[str] = mapped_column(String(100))
    file_size: Mapped[int] = mapped_column(Integer)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    lesson = relationship("Lesson", back_populates="materials")


class Enrollment(Base):
    """
    One client's enrollment in one course.

    Unique on (course_id, client_id) so a client can't be enrolled twice; the
    enroll endpoint turns that constraint into a 409 (or returns the existing
    row) rather than a database error.

    `invoice_id` is set for paid courses only. When that invoice is marked
    PAID, `services.notifications.notify_course_access_active` flips the
    enrollment to ACTIVE and emails the student -- the hook is in
    `api/v1/invoices.record_payment`, non-fatal like every other emit.
    """

    __tablename__ = "enrollments"
    __table_args__ = (
        UniqueConstraint("course_id", "client_id", name="uq_enrollments_course_client"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"), index=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    invoice_id: Mapped[int | None] = mapped_column(
        ForeignKey("invoices.id"), nullable=True, index=True
    )

    status: Mapped[EnrollmentStatus] = mapped_column(
        Enum(EnrollmentStatus), default=EnrollmentStatus.PENDING_PAYMENT, index=True
    )

    enrolled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    # Set by the daily reminder sweep (app.send_course_reminders) so a student
    # gets at most one "continue your course" email a week.
    last_reminder_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    # Set once, when progress first reaches 100% -- drives the one-time
    # "your certificate is ready" email.
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)

    course = relationship("Course", back_populates="enrollments")
    client = relationship("User", foreign_keys=[client_id])
    invoice = relationship("Invoice")
    progress = relationship(
        "LessonProgress", back_populates="enrollment", cascade="all, delete-orphan"
    )


class LessonProgress(Base):
    """One row per completed lesson per enrollment. Unique by that pair."""

    __tablename__ = "lesson_progress"
    __table_args__ = (
        UniqueConstraint("enrollment_id", "lesson_id", name="uq_lesson_progress"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    enrollment_id: Mapped[int] = mapped_column(ForeignKey("enrollments.id"), index=True)
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lessons.id"), index=True)
    completed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    enrollment = relationship("Enrollment", back_populates="progress")
    lesson = relationship("Lesson")


class LessonQuizQuestion(Base):
    """
    One multiple-choice question in a lesson's quiz.

    `options` is a JSON list of answer strings; `correct_index` points into it.
    The correct answer and explanation never leave the server until the student
    submits -- the client endpoint strips them from the question list.
    """

    __tablename__ = "lesson_quiz_questions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lessons.id"), index=True)
    question: Mapped[str] = mapped_column(Text)
    options: Mapped[list] = mapped_column(JSON)
    correct_index: Mapped[int] = mapped_column(Integer)
    explanation: Mapped[str] = mapped_column(Text, default="")
    display_order: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    lesson = relationship("Lesson", back_populates="quiz_questions")


class LessonQuizAttempt(Base):
    """
    One submitted attempt at a lesson quiz. Every attempt is kept (retries are
    allowed); the best score is what the player shows.
    """

    __tablename__ = "lesson_quiz_attempts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    enrollment_id: Mapped[int] = mapped_column(ForeignKey("enrollments.id"), index=True)
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lessons.id"), index=True)
    score: Mapped[int] = mapped_column(Integer)
    total: Mapped[int] = mapped_column(Integer)
    passed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
