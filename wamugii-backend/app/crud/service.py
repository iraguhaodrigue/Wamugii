import re

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.service import Service
from app.schemas.service import ServiceCreate, ServiceUpdate

_SLUG_RE = re.compile(r"[^a-z0-9]+")


def slugify(value: str) -> str:
    slug = _SLUG_RE.sub("-", value.lower()).strip("-")
    return slug or "service"


def _unique_slug(db: Session, base_slug: str, exclude_id: int | None = None) -> str:
    slug = base_slug
    suffix = 2
    while True:
        query = select(Service.id).where(Service.slug == slug)
        if exclude_id is not None:
            query = query.where(Service.id != exclude_id)
        if db.scalar(query) is None:
            return slug
        slug = f"{base_slug}-{suffix}"
        suffix += 1


def get_by_id(db: Session, service_id: int) -> Service | None:
    return db.get(Service, service_id)


def get_by_slug(db: Session, slug: str) -> Service | None:
    return db.scalar(select(Service).where(Service.slug == slug))


def list_services(
    db: Session,
    *,
    limit: int = 20,
    offset: int = 0,
    category: str | None = None,
    search: str | None = None,
    include_inactive: bool = False,
) -> list[Service]:
    query = select(Service)
    if not include_inactive:
        query = query.where(Service.is_active.is_(True))
    if category:
        query = query.where(Service.category == category)
    if search:
        query = query.where(func.lower(Service.name).contains(search.lower()))
    query = query.order_by(Service.display_order, Service.id).offset(offset).limit(limit)
    return list(db.scalars(query).all())


def create(db: Session, data: ServiceCreate) -> Service:
    base_slug = slugify(data.slug or data.name)
    slug = _unique_slug(db, base_slug)
    service = Service(**data.model_dump(exclude={"slug"}), slug=slug)
    db.add(service)
    db.commit()
    db.refresh(service)
    return service


def update(db: Session, service: Service, data: ServiceUpdate) -> Service:
    updates = data.model_dump(exclude_unset=True)
    if updates.get("slug"):
        updates["slug"] = _unique_slug(db, slugify(updates["slug"]), exclude_id=service.id)
    else:
        updates.pop("slug", None)
    for field, value in updates.items():
        setattr(service, field, value)
    db.commit()
    db.refresh(service)
    return service


def count_total(db: Session) -> int:
    return db.scalar(select(func.count()).select_from(Service)) or 0


def count_active(db: Session) -> int:
    return (
        db.scalar(select(func.count()).select_from(Service).where(Service.is_active.is_(True)))
        or 0
    )


def soft_delete(db: Session, service: Service) -> Service:
    service.is_active = False
    db.commit()
    db.refresh(service)
    return service
