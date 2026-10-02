import enum
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class QuestionType(str, enum.Enum):
    TEXT = "TEXT"
    TEXTAREA = "TEXTAREA"
    NUMBER = "NUMBER"
    SELECT = "SELECT"
    MULTISELECT = "MULTISELECT"
    YES_NO = "YES_NO"


# The only two types whose `options` list means anything. Validated in
# schemas/service_question.py so a SELECT can't be created with no choices.
CHOICE_TYPES = (QuestionType.SELECT, QuestionType.MULTISELECT)


class ServiceQuestion(Base):
    """
    One custom question on one service.

    This is what makes the public quote form adapt: a web project asks about
    pages and features, a research project about topic and scope. The form
    fetches a service's active questions when that service is chosen.

    `options` holds a JSON-encoded list of strings for SELECT/MULTISELECT, as
    Text rather than a JSON column so the same migration runs on SQLite and
    PostgreSQL. The API takes and returns a real list -- the encoding is handled
    in `schemas/service_question.py` and `crud/service_question.py`, so nothing
    above those two files deals in JSON strings.
    """

    __tablename__ = "service_questions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    service_id: Mapped[int] = mapped_column(ForeignKey("services.id"), index=True)

    question_text: Mapped[str] = mapped_column(String(500))
    question_type: Mapped[QuestionType] = mapped_column(
        Enum(QuestionType), default=QuestionType.TEXT, index=True
    )
    options: Mapped[str | None] = mapped_column(Text, nullable=True)

    is_required: Mapped[bool] = mapped_column(Boolean, default=False)
    display_order: Mapped[int] = mapped_column(Integer, default=0, index=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    service = relationship("Service", back_populates="questions")
