from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.service_question import ServiceQuestion
from app.schemas.json_list import dump_json_list
from app.schemas.service_question import ServiceQuestionCreate, ServiceQuestionUpdate


def get_by_id_for_service(
    db: Session, question_id: int, service_id: int
) -> ServiceQuestion | None:
    """Scoped lookup: a question id from another service reads as missing (404)."""
    return db.scalar(
        select(ServiceQuestion).where(
            ServiceQuestion.id == question_id, ServiceQuestion.service_id == service_id
        )
    )


def list_for_service(
    db: Session, service_id: int, *, include_inactive: bool = False
) -> list[ServiceQuestion]:
    query = select(ServiceQuestion).where(ServiceQuestion.service_id == service_id)
    if not include_inactive:
        query = query.where(ServiceQuestion.is_active.is_(True))
    return list(
        db.scalars(
            query.order_by(ServiceQuestion.display_order, ServiceQuestion.id)
        ).all()
    )


def list_required_for_service(db: Session, service_id: int) -> list[ServiceQuestion]:
    """The active, required questions a submission for this service must answer."""
    return [q for q in list_for_service(db, service_id) if q.is_required]


def create(
    db: Session, service_id: int, data: ServiceQuestionCreate
) -> ServiceQuestion:
    question = ServiceQuestion(
        service_id=service_id,
        question_text=data.question_text.strip(),
        question_type=data.question_type,
        options=dump_json_list(data.options),
        is_required=data.is_required,
        display_order=data.display_order,
    )
    db.add(question)
    db.commit()
    db.refresh(question)
    return question


def update(
    db: Session, question: ServiceQuestion, data: ServiceQuestionUpdate
) -> ServiceQuestion:
    """
    Applies only the fields that were sent. `options` is re-encoded on its way
    in; the router has already checked the merged type/options pair is coherent.
    """
    updates = data.model_dump(exclude_unset=True)
    if "options" in updates:
        updates["options"] = dump_json_list(updates["options"])
    if "question_text" in updates and updates["question_text"]:
        updates["question_text"] = updates["question_text"].strip()
    for field, value in updates.items():
        setattr(question, field, value)
    db.commit()
    db.refresh(question)
    return question


def deactivate(db: Session, question: ServiceQuestion) -> ServiceQuestion:
    """
    Soft delete. Quotes already submitted keep their answers and their stored
    question text, so removing a question never rewrites history.
    """
    question.is_active = False
    db.commit()
    db.refresh(question)
    return question
