from datetime import date, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.domain import Domain, DomainStatus
from app.schemas.domain import DomainCreate, DomainUpdate


def get_domain(db: Session, domain_id: int) -> Domain | None:
    return db.get(Domain, domain_id)


def get_domain_for_client(db: Session, domain_id: int, client_id: int) -> Domain | None:
    """None for anything that isn't this client's, which the router turns into 404."""
    return db.scalar(
        select(Domain).where(
            Domain.id == domain_id,
            Domain.client_id == client_id,
            Domain.is_active.is_(True),
        )
    )


def list_domains(
    db: Session,
    *,
    limit: int = 20,
    offset: int = 0,
    status: DomainStatus | None = None,
    client_id: int | None = None,
    search: str | None = None,
    include_inactive: bool = False,
) -> list[Domain]:
    query = select(Domain)
    if not include_inactive:
        query = query.where(Domain.is_active.is_(True))
    if status is not None:
        query = query.where(Domain.status == status)
    if client_id is not None:
        query = query.where(Domain.client_id == client_id)
    if search:
        query = query.where(func.lower(Domain.domain_name).contains(search.lower()))
    query = query.order_by(Domain.created_at.desc()).offset(offset).limit(limit)
    return list(db.scalars(query).all())


def list_domains_for_client(
    db: Session, client_id: int, *, include_inactive: bool = False
) -> list[Domain]:
    query = select(Domain).where(Domain.client_id == client_id)
    if not include_inactive:
        query = query.where(Domain.is_active.is_(True))
    return list(db.scalars(query.order_by(Domain.created_at.desc())).all())


def create_domain(db: Session, data: DomainCreate) -> Domain:
    domain = Domain(**data.model_dump())
    db.add(domain)
    db.commit()
    db.refresh(domain)
    return domain


def update_domain(db: Session, domain: Domain, data: DomainUpdate) -> Domain:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(domain, field, value)
    db.commit()
    db.refresh(domain)
    return domain


def deactivate_domain(db: Session, domain: Domain) -> Domain:
    domain.is_active = False
    db.commit()
    db.refresh(domain)
    return domain


def get_domains_expiring_soon(db: Session, days: int = 30) -> list[Domain]:
    """
    Active domains expiring within `days`.

    For an admin view or a future reminder job — nothing runs it on a schedule,
    since this project has no scheduler and renewal is a manual action.
    """
    today = date.today()
    horizon = today + timedelta(days=days)
    return list(
        db.scalars(
            select(Domain)
            .where(
                Domain.is_active.is_(True),
                Domain.status == DomainStatus.ACTIVE,
                Domain.expires_at.is_not(None),
                Domain.expires_at >= today,
                Domain.expires_at <= horizon,
            )
            .order_by(Domain.expires_at.asc())
        ).all()
    )


def count_active_domains(db: Session) -> int:
    return (
        db.scalar(
            select(func.count())
            .select_from(Domain)
            .where(Domain.status == DomainStatus.ACTIVE, Domain.is_active.is_(True))
        )
        or 0
    )
