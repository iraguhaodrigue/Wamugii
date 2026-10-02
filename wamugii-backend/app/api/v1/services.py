import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import DbDep, OptionalUser, require_roles
from app.crud import service as service_crud
from app.crud import service_question as question_crud
from app.models.service import Service
from app.models.service_question import ServiceQuestion
from app.models.user import Role, User
from app.schemas.service import ServiceCreate, ServiceRead, ServiceUpdate
from app.schemas.service_question import (
    ServiceQuestionCreate,
    ServiceQuestionRead,
    ServiceQuestionUpdate,
)

router = APIRouter(prefix="/services", tags=["services"])
logger = logging.getLogger(__name__)


def _is_staff(user: User | None) -> bool:
    return user is not None and user.role in (Role.ADMIN, Role.STAFF)


@router.get("", response_model=list[ServiceRead])
def list_services(
    db: DbDep,
    current_user: OptionalUser,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    category: str | None = None,
    search: str | None = None,
    include_inactive: bool = False,
):
    include_inactive = include_inactive and _is_staff(current_user)
    return service_crud.list_services(
        db,
        limit=limit,
        offset=offset,
        category=category,
        search=search,
        include_inactive=include_inactive,
    )


@router.get("/{service_id}", response_model=ServiceRead)
def get_service(service_id: int, db: DbDep, current_user: OptionalUser):
    service = service_crud.get_by_id(db, service_id)
    if not service or (not service.is_active and not _is_staff(current_user)):
        raise HTTPException(status_code=404, detail="Service not found")
    return service


@router.post(
    "",
    response_model=ServiceRead,
    status_code=201,
    dependencies=[Depends(require_roles(Role.ADMIN, Role.STAFF))],
)
def create_service(data: ServiceCreate, db: DbDep):
    return service_crud.create(db, data)


@router.patch(
    "/{service_id}",
    response_model=ServiceRead,
    dependencies=[Depends(require_roles(Role.ADMIN, Role.STAFF))],
)
def update_service(service_id: int, data: ServiceUpdate, db: DbDep):
    service = service_crud.get_by_id(db, service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service_crud.update(db, service, data)


@router.delete(
    "/{service_id}",
    response_model=ServiceRead,
    dependencies=[Depends(require_roles(Role.ADMIN, Role.STAFF))],
)
def delete_service(service_id: int, db: DbDep):
    service = service_crud.get_by_id(db, service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service_crud.soft_delete(db, service)


# --- per-service quote questions --------------------------------------------
#
# These drive the public quote form: when a visitor picks a service, the form
# fetches that service's active questions and renders them. Admin/staff manage
# them; the read is public because the form is public.


def _get_service_or_404(db: Session, service_id: int) -> Service:
    service = service_crud.get_by_id(db, service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service


def _get_question_or_404(db: Session, service_id: int, question_id: int) -> ServiceQuestion:
    question = question_crud.get_by_id_for_service(db, question_id, service_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return question


@router.get(
    "/{service_id}/questions",
    response_model=list[ServiceQuestionRead],
    tags=["service-questions"],
    summary="List a service's quote questions (public; active only unless staff)",
)
def list_service_questions(
    service_id: int,
    db: DbDep,
    current_user: OptionalUser,
    include_inactive: bool = False,
):
    """
    Open, because the quote form is open.

    `include_inactive` is honoured only for staff -- the same shape as
    `list_services` -- so the admin screen can show soft-deleted questions
    through this one endpoint while the public form only ever sees live ones.
    An inactive service is a 404 for anyone but staff, matching `get_service`,
    so a draft service's questions aren't discoverable before it is published.
    """
    service = service_crud.get_by_id(db, service_id)
    if not service or (not service.is_active and not _is_staff(current_user)):
        raise HTTPException(status_code=404, detail="Service not found")

    include_inactive = include_inactive and _is_staff(current_user)
    return question_crud.list_for_service(db, service_id, include_inactive=include_inactive)


@router.post(
    "/{service_id}/questions",
    response_model=ServiceQuestionRead,
    status_code=201,
    dependencies=[Depends(require_roles(Role.ADMIN, Role.STAFF))],
    tags=["service-questions"],
    summary="Add a quote question to a service (ADMIN or STAFF)",
)
def create_service_question(service_id: int, data: ServiceQuestionCreate, db: DbDep):
    _get_service_or_404(db, service_id)
    question = question_crud.create(db, service_id, data)
    logger.info("question %s added to service %s", question.id, service_id)
    return question


@router.patch(
    "/{service_id}/questions/{question_id}",
    response_model=ServiceQuestionRead,
    dependencies=[Depends(require_roles(Role.ADMIN, Role.STAFF))],
    tags=["service-questions"],
    summary="Edit a service's quote question (ADMIN or STAFF)",
)
def update_service_question(
    service_id: int, question_id: int, data: ServiceQuestionUpdate, db: DbDep
):
    """
    A partial update can still produce an incoherent question -- switching a
    TEXT question to SELECT without sending options, or the reverse -- so the
    merged result is re-validated against the full create schema before it is
    written.
    """
    _get_service_or_404(db, service_id)
    question = _get_question_or_404(db, service_id, question_id)

    sent = data.model_dump(exclude_unset=True)
    merged = {
        "question_text": sent.get("question_text", question.question_text),
        "question_type": sent.get("question_type", question.question_type),
        "options": sent["options"] if "options" in sent else question.options,
        "is_required": sent.get("is_required", question.is_required),
        "display_order": sent.get("display_order", question.display_order),
    }
    try:
        ServiceQuestionCreate.model_validate(merged)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return question_crud.update(db, question, data)


@router.delete(
    "/{service_id}/questions/{question_id}",
    response_model=ServiceQuestionRead,
    dependencies=[Depends(require_roles(Role.ADMIN, Role.STAFF))],
    tags=["service-questions"],
    summary="Soft-delete a service's quote question (ADMIN or STAFF)",
)
def delete_service_question(service_id: int, question_id: int, db: DbDep):
    """
    Soft delete. Quotes already submitted keep their answers and the question
    text as it read at submit time, so this never rewrites past submissions.
    """
    _get_service_or_404(db, service_id)
    question = _get_question_or_404(db, service_id, question_id)
    return question_crud.deactivate(db, question)
