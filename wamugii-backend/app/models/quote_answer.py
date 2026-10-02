from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class QuoteAnswer(Base):
    """
    One answer on one submitted quote request.

    `question_text` is stored as submitted rather than read through the FK. A
    question can be reworded or soft-deleted months later, and the quote has to
    keep showing what was actually asked at the time -- otherwise an archived
    quote silently re-labels itself and staff read the wrong thing. The FK is
    kept alongside it for grouping and reporting.

    `question_id` is nullable for two reasons: historic quotes predate questions
    entirely, and a submission can carry a detail the form captured without a
    configured question behind it (the chosen hosting plan, for instance), which
    then travels with the quote as a normal answer instead of being lost.

    No `is_active` flag: an answer is part of the submission record, so it is
    never removed on its own. Soft-deleting the quote hides the whole thing.
    """

    __tablename__ = "quote_answers"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    quote_request_id: Mapped[int] = mapped_column(ForeignKey("quote_requests.id"), index=True)
    question_id: Mapped[int | None] = mapped_column(
        ForeignKey("service_questions.id"), nullable=True, index=True
    )

    question_text: Mapped[str] = mapped_column(String(500))
    answer: Mapped[str] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    quote_request = relationship("QuoteRequest", back_populates="answers")
    question = relationship("ServiceQuestion")
