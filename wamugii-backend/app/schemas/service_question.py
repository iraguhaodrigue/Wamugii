from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.models.service_question import CHOICE_TYPES, QuestionType
from app.schemas.json_list import parse_json_list


class ServiceQuestionBase(BaseModel):
    question_text: str = Field(min_length=1, max_length=500)
    question_type: QuestionType = QuestionType.TEXT
    options: list[str] | None = None
    is_required: bool = False
    display_order: int = 0

    # Accepts a real list on the way in and the stored JSON string on the way
    # out -- see schemas/json_list.py.
    _parse_options = field_validator("options", mode="before")(parse_json_list)

    @model_validator(mode="after")
    def _check_options_match_the_type(self):
        """
        A SELECT with no choices is an unanswerable question, and options on a
        free-text question are dead data that would confuse the form renderer.
        Both are rejected here rather than being silently tolerated.
        """
        if self.question_type in CHOICE_TYPES:
            if not self.options or len(self.options) < 1:
                raise ValueError(
                    f"{self.question_type.value} questions need at least one entry in `options`"
                )
        elif self.options:
            raise ValueError(
                f"`options` only applies to {' / '.join(t.value for t in CHOICE_TYPES)} questions"
            )
        return self


class ServiceQuestionCreate(ServiceQuestionBase):
    pass


class ServiceQuestionUpdate(BaseModel):
    """
    Every field optional, but a type/options change has to stay consistent, so
    the router re-validates the merged result against `ServiceQuestionBase`
    rather than trusting a partial payload on its own.
    """

    question_text: str | None = Field(default=None, min_length=1, max_length=500)
    question_type: QuestionType | None = None
    options: list[str] | None = None
    is_required: bool | None = None
    display_order: int | None = None
    is_active: bool | None = None

    _parse_options = field_validator("options", mode="before")(parse_json_list)


class ServiceQuestionRead(ServiceQuestionBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    service_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
