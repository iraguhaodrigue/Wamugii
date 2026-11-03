"""Final exams, instructors and lesson Q&A."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.course import ExamAttemptStatus, ExamQuestionKind


# --- exam rules -------------------------------------------------------------


class ExamSettings(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    exam_question_count: int = Field(ge=5, le=200)
    exam_minutes: int = Field(ge=5, le=300)
    exam_pass_percent: int = Field(ge=1, le=100)
    exam_max_attempts: int = Field(ge=1, le=20)
    exam_cooldown_hours: int = Field(ge=0, le=720)
    exam_max_leaves: int = Field(ge=1, le=20)


class ExamSettingsUpdate(BaseModel):
    exam_question_count: int | None = Field(default=None, ge=5, le=200)
    exam_minutes: int | None = Field(default=None, ge=5, le=300)
    exam_pass_percent: int | None = Field(default=None, ge=1, le=100)
    exam_max_attempts: int | None = Field(default=None, ge=1, le=20)
    exam_cooldown_hours: int | None = Field(default=None, ge=0, le=720)
    exam_max_leaves: int | None = Field(default=None, ge=1, le=20)


# --- question bank (management) --------------------------------------------


class ExamQuestionWrite(BaseModel):
    """
    One bank question. `correct` is option indexes for SINGLE / MULTIPLE /
    TRUE_FALSE and the accepted answers for FILL_BLANK.
    """

    kind: ExamQuestionKind
    question: str = Field(min_length=3, max_length=4000)
    options: list[str] = Field(default_factory=list, max_length=8)
    correct: list[int | str] = Field(min_length=1, max_length=10)
    explanation: str = Field(default="", max_length=4000)
    topic: str | None = Field(default=None, max_length=255)
    is_active: bool = True

    @model_validator(mode="after")
    def _check_shape(self):
        k = self.kind
        if k == ExamQuestionKind.TRUE_FALSE:
            self.options = ["True", "False"]
        if k in (ExamQuestionKind.SINGLE, ExamQuestionKind.MULTIPLE, ExamQuestionKind.TRUE_FALSE):
            opts = [o.strip() for o in self.options]
            if len(opts) < 2 or any(not o for o in opts):
                raise ValueError("Choice questions need at least 2 non-empty options")
            self.options = opts
            try:
                idx = sorted({int(c) for c in self.correct})
            except (TypeError, ValueError) as exc:
                raise ValueError("`correct` must be option numbers (0 = first option)") from exc
            if any(i < 0 or i >= len(opts) for i in idx):
                raise ValueError("A correct option number is out of range")
            if k in (ExamQuestionKind.SINGLE, ExamQuestionKind.TRUE_FALSE) and len(idx) != 1:
                raise ValueError("Single-answer and true/false questions have exactly one correct option")
            if k == ExamQuestionKind.MULTIPLE and len(idx) < 2:
                raise ValueError("A multiple-answer question needs at least 2 correct options")
            self.correct = idx
        else:  # FILL_BLANK
            answers = [str(c).strip() for c in self.correct if str(c).strip()]
            if not answers:
                raise ValueError("A fill-in-the-blank question needs at least one accepted answer")
            if "___" not in self.question:
                raise ValueError("Mark the blank in the sentence with ___ (three underscores)")
            self.options = []
            self.correct = answers
        return self


class ExamQuestionAdmin(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    course_id: int
    kind: ExamQuestionKind
    question: str
    options: list[str]
    correct: list[int | str]
    explanation: str
    topic: str | None
    is_active: bool
    created_at: datetime


class ExamBankSummary(BaseModel):
    settings: ExamSettings
    questions: list[ExamQuestionAdmin]
    counts: dict[str, int]
    ai_drafting_available: bool = False


class AiDraftRequest(BaseModel):
    lesson_ids: list[int] = Field(default_factory=list, max_length=30)
    count: int = Field(default=10, ge=1, le=30)
    kinds: list[ExamQuestionKind] = Field(
        default_factory=lambda: list(ExamQuestionKind), min_length=1
    )


class AiDraftResponse(BaseModel):
    drafts: list[ExamQuestionWrite]
    note: str = ""


# --- the exam, student side --------------------------------------------------


class ExamAttemptSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: ExamAttemptStatus
    started_at: datetime
    submitted_at: datetime | None
    submit_reason: str | None
    score: int | None
    total: int
    percent: int | None
    passed: bool
    leave_count: int


class ExamOverview(BaseModel):
    available: bool                 # the course has an exam at all
    eligible: bool                  # the student may start an attempt right now
    reason: str = ""                # why not, in plain words
    lessons_complete: bool
    question_count: int
    minutes: int
    pass_percent: int
    max_attempts: int
    attempts_used: int
    attempts_left: int
    next_attempt_at: datetime | None = None
    max_leaves: int
    passed: bool
    best_percent: int | None = None
    in_progress_attempt_id: int | None = None
    type_counts: dict[str, int] = {}
    attempts: list[ExamAttemptSummary] = []


class ExamOption(BaseModel):
    id: int          # the option's index in the stored question
    text: str


class ExamQuestionPublic(BaseModel):
    id: int
    number: int
    kind: ExamQuestionKind
    question: str
    options: list[ExamOption] = []


class ExamSession(BaseModel):
    attempt_id: int
    course_id: int
    course_title: str
    started_at: datetime
    deadline_at: datetime
    server_now: datetime
    leave_count: int
    max_leaves: int
    pass_percent: int
    questions: list[ExamQuestionPublic]
    answers: dict[str, int | list[int] | str | None] = {}


class ExamAnswersSave(BaseModel):
    # question id (as a string, JSON keys are strings) -> answer
    answers: dict[str, int | list[int] | str | None] = Field(max_length=300)


class ExamEvent(BaseModel):
    # "leave" counts against exam_max_leaves; "notice" is only logged.
    type: str = Field(pattern="^(leave|notice)$")
    detail: str = Field(default="", max_length=60)


class TopicScore(BaseModel):
    topic: str
    correct: int
    total: int


class ExamResult(BaseModel):
    attempt_id: int
    score: int
    total: int
    percent: int
    pass_percent: int
    passed: bool
    submit_reason: str
    topic_scores: list[TopicScore] = []
    attempts_left: int
    next_attempt_at: datetime | None = None
    certificate_ready: bool = False


class ExamEventResult(BaseModel):
    leave_count: int
    max_leaves: int
    submitted: bool
    result: ExamResult | None = None


class ExamAttemptAdmin(ExamAttemptSummary):
    """Management view: who, when, score, and every proctoring event."""

    client_id: int
    enrollment_id: int
    student_name: str = ""
    student_email: str = ""
    events: list[dict] = []
    topic_scores: list[TopicScore] | None = None


# --- instructors ---------------------------------------------------------------


class InstructorAssign(BaseModel):
    email: str = Field(min_length=3, max_length=255)


class InstructorRead(BaseModel):
    user_id: int
    full_name: str
    email: str
    assigned_at: datetime


class InstructorCourseRead(BaseModel):
    id: int
    title: str
    slug: str
    status: str
    lesson_count: int
    student_count: int
    unanswered_questions: int
    exam_question_count: int


# --- lesson Q&A -----------------------------------------------------------------


class LessonQuestionCreate(BaseModel):
    body: str = Field(min_length=3, max_length=4000)


class LessonAnswerCreate(BaseModel):
    body: str = Field(min_length=1, max_length=4000)


class LessonAnswerRead(BaseModel):
    id: int
    body: str
    author_name: str
    author_role: str          # "Instructor", "WAMUGII team" or "Student"
    created_at: datetime


class LessonQuestionRead(BaseModel):
    id: int
    course_id: int
    lesson_id: int
    lesson_title: str = ""
    body: str
    author_name: str
    is_mine: bool = False
    created_at: datetime
    answered_by_instructor: bool = False
    answers: list[LessonAnswerRead] = []
