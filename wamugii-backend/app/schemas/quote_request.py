from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator

from app.models.quote_request import QuoteStatus


class QuoteAnswerSubmit(BaseModel):
    """
    One answer in a public submission.

    `question_id` points at a configured question on the chosen service; the
    router checks it really belongs to that service and captures the question
    text itself, so a caller cannot relabel a question by sending their own
    text alongside an id.

    Leaving `question_id` out is the escape hatch for a detail the form
    captured without a configured question behind it -- the chosen hosting plan,
    for instance. `question_text` is then required, because otherwise the answer
    would arrive with nothing saying what it answers.
    """

    question_id: int | None = None
    question_text: str | None = Field(default=None, max_length=500)
    answer: str = Field(max_length=10_000)

    @model_validator(mode="after")
    def _label_required_without_a_question(self):
        if self.question_id is None and not (self.question_text or "").strip():
            raise ValueError("question_text is required when question_id is omitted")
        return self


class QuoteAnswerRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    question_id: int | None
    # As asked at submit time, not as the question reads today -- see
    # models/quote_answer.py.
    question_text: str
    answer: str


class QuoteRequestCreate(BaseModel):
    full_name: str
    email: EmailStr
    phone: str
    company_name: str | None = None
    service_id: int | None = None
    project_title: str
    project_description: str
    budget_range: str | None = None
    preferred_deadline: str | None = None
    # Optional throughout: a service with no questions, or no service at all,
    # submits exactly as it did before this field existed.
    answers: list[QuoteAnswerSubmit] = []


class QuoteRequestPublicRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    email: EmailStr
    phone: str
    company_name: str | None
    service_id: int | None
    project_title: str
    project_description: str
    budget_range: str | None
    preferred_deadline: str | None
    status: QuoteStatus
    created_at: datetime
    answers: list[QuoteAnswerRead] = []


class QuoteRequestRead(QuoteRequestPublicRead):
    admin_notes: str | None
    is_active: bool
    updated_at: datetime


class QuoteRequestAdminUpdate(BaseModel):
    status: QuoteStatus | None = None
    admin_notes: str | None = None
