from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.course import CourseStatus, EnrollmentStatus

# Reused in two places so the price rule lives once.
MAX_PRICE = Decimal("100000000")


class CourseCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    slug: str | None = None
    description: str = Field(default="")
    cover_image_url: str | None = Field(default=None, max_length=500)
    category: str | None = Field(default=None, max_length=100)
    is_free: bool = True
    price: Decimal | None = Field(default=None, ge=0, le=MAX_PRICE)
    status: CourseStatus = CourseStatus.DRAFT
    display_order: int = 0

    @model_validator(mode="after")
    def _price_matches_is_free(self):
        """
        A paid course needs a price > 0; a free course must not carry one.

        Keeps the two columns consistent before anything is written -- a paid
        course with `price` null would otherwise land in the enroll flow and
        try to create a zero-amount invoice.
        """
        if self.is_free:
            self.price = None
            return self
        if self.price is None or self.price <= 0:
            raise ValueError("A paid course needs price > 0")
        return self


class CourseUpdate(BaseModel):
    """
    Every field optional; `is_free` / `price` are revalidated on the merged
    row in the router so a partial update can't produce an inconsistent pair.
    """

    title: str | None = Field(default=None, min_length=1, max_length=255)
    slug: str | None = None
    description: str | None = None
    cover_image_url: str | None = Field(default=None, max_length=500)
    category: str | None = Field(default=None, max_length=100)
    is_free: bool | None = None
    price: Decimal | None = Field(default=None, ge=0, le=MAX_PRICE)
    status: CourseStatus | None = None
    display_order: int | None = None
    is_active: bool | None = None


class CourseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    slug: str
    description: str
    cover_image_url: str | None
    category: str | None
    is_free: bool
    price: Decimal | None
    status: CourseStatus
    display_order: int
    is_active: bool
    lesson_count: int = 0
    created_at: datetime
    updated_at: datetime


class LessonBrief(BaseModel):
    """
    Public lesson view -- title only. Content and video_url are deliberately
    absent: the catalog teases what's inside, enrolled content is served
    through `/client/courses/.../lessons/{id}`.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    display_order: int


class CoursePublicDetail(CourseRead):
    """What the public course detail page gets. Lesson titles, nothing more."""

    lessons: list[LessonBrief] = []


class LessonCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    content: str = Field(default="")
    video_url: str | None = Field(default=None, max_length=500)
    display_order: int = 0


class LessonUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    content: str | None = None
    video_url: str | None = Field(default=None, max_length=500)
    display_order: int | None = None
    is_active: bool | None = None


class LessonMaterialRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    lesson_id: int
    original_filename: str
    content_type: str
    file_size: int
    created_at: datetime


class LessonRead(BaseModel):
    """Full lesson view, including materials. Served only to enrolled clients."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    course_id: int
    title: str
    content: str
    video_url: str | None
    display_order: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    materials: list[LessonMaterialRead] = []


class EnrollmentRead(BaseModel):
    """
    Admin view of one enrollment. Progress is served alongside so the admin
    enrollments list on a course can show how far each student has got.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    course_id: int
    client_id: int
    invoice_id: int | None
    status: EnrollmentStatus
    enrolled_at: datetime
    is_active: bool

    # Filled in by the router from the related rows.
    completed_lessons: int = 0
    total_lessons: int = 0
    progress_percent: int = 0


class ClientEnrollmentRead(EnrollmentRead):
    """
    The client's own view of their enrollment, with the course title and the
    `complete payment to unlock` hint for paid courses the invoice isn't paid
    for yet. No admin-level fields beyond what they already know about
    themselves.
    """

    # Filled in by the client router from the related course row, so
    # `model_validate(enrollment)` succeeds first and the fields are set
    # afterwards -- same pattern as `completed_lessons` et al above.
    course_title: str = ""
    course_slug: str = ""
    is_free: bool = False


class EnrollResponse(BaseModel):
    """
    Shape returned by POST /client/courses/{id}/enroll.

    `message` is the one line a UI shows ("You're enrolled" vs "complete
    payment to unlock"), so a client can act without having to decode the
    status enum itself.
    """

    enrollment: ClientEnrollmentRead
    message: str


class LessonCompleteResponse(BaseModel):
    """What the mark-complete endpoint returns -- just the new progress."""

    completed_lessons: int
    total_lessons: int
    progress_percent: int


class CertificateRead(BaseModel):
    """
    A certificate of completion. Computed from the enrollment's progress on
    every request rather than stored: there is no certificate record to go
    stale, and revoking one is just a matter of the progress no longer being
    complete (a lesson added to the course re-opens it).

    `certificate_id` is derived from the enrollment id, so the same student on
    the same course always gets the same number back.
    """

    student_name: str
    course_title: str
    course_slug: str
    lesson_count: int
    certificate_id: str
    issued_on: date
