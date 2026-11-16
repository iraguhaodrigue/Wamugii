from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class ReviewWrite(BaseModel):
    rating: int = Field(ge=1, le=5)
    comment: str | None = Field(default=None, max_length=1000)

    @field_validator("comment")
    @classmethod
    def _tidy(cls, v: str | None) -> str | None:
        """Trim spaces; an empty comment means a rating without a comment."""
        if v is None:
            return None
        v = "\n".join(line.rstrip() for line in v.strip().splitlines())
        return v or None


class ReviewPublic(BaseModel):
    """What everyone sees: first name and initial only, never the email."""

    id: int
    rating: int
    comment: str | None
    reviewer_name: str
    created_at: datetime
    updated_at: datetime


class RatingSummary(BaseModel):
    average: float | None = None
    count: int = 0
    # Number of ratings per star, "5" down to "1".
    distribution: dict[str, int] = Field(default_factory=dict)


class CourseReviewsPage(BaseModel):
    summary: RatingSummary
    reviews: list[ReviewPublic]
    total_with_comments: int


class MyReviewStatus(BaseModel):
    """For the student: their own review (if any) and whether they may write one."""

    review: ReviewPublic | None = None
    can_review: bool
    reason: str | None = None
    completed_lessons: int = 0
    lessons_needed: int = 0


class ReviewAdminRead(ReviewPublic):
    user_id: int
    reviewer_full_name: str
    is_hidden: bool


class ReviewModerate(BaseModel):
    is_hidden: bool


class HandbookInfo(BaseModel):
    pages: int
    words: int
    chapters: int
    sample_available: bool = False
