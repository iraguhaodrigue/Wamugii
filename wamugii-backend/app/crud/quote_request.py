from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.quote_request import QuoteRequest, QuoteStatus
from app.schemas.quote_request import QuoteRequestAdminUpdate, QuoteRequestCreate


def get_by_id(db: Session, quote_id: int) -> QuoteRequest | None:
    return db.get(QuoteRequest, quote_id)


def list_quote_requests(
    db: Session,
    *,
    limit: int = 20,
    offset: int = 0,
    status: QuoteStatus | None = None,
    service_id: int | None = None,
    search: str | None = None,
    include_inactive: bool = False,
) -> list[QuoteRequest]:
    query = select(QuoteRequest)
    if not include_inactive:
        query = query.where(QuoteRequest.is_active.is_(True))
    if status is not None:
        query = query.where(QuoteRequest.status == status)
    if service_id is not None:
        query = query.where(QuoteRequest.service_id == service_id)
    if search:
        term = search.lower()
        query = query.where(
            func.lower(QuoteRequest.full_name).contains(term)
            | func.lower(QuoteRequest.email).contains(term)
            | func.lower(QuoteRequest.project_title).contains(term)
        )
    query = query.order_by(QuoteRequest.created_at.desc()).offset(offset).limit(limit)
    return list(db.scalars(query).all())


def create(db: Session, data: QuoteRequestCreate) -> QuoteRequest:
    quote = QuoteRequest(**data.model_dump(), status=QuoteStatus.NEW)
    db.add(quote)
    db.commit()
    db.refresh(quote)
    return quote


def update_admin_fields(
    db: Session, quote: QuoteRequest, data: QuoteRequestAdminUpdate
) -> QuoteRequest:
    updates = data.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(quote, field, value)
    db.commit()
    db.refresh(quote)
    return quote


def soft_delete(db: Session, quote: QuoteRequest) -> QuoteRequest:
    quote.is_active = False
    db.commit()
    db.refresh(quote)
    return quote


def count_pending(db: Session) -> int:
    return (
        db.scalar(
            select(func.count())
            .select_from(QuoteRequest)
            .where(
                QuoteRequest.status.in_([QuoteStatus.NEW, QuoteStatus.REVIEWING]),
                QuoteRequest.is_active.is_(True),
            )
        )
        or 0
    )
