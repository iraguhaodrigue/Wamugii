from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.domain_extension import DomainExtension
from app.schemas.domain_extension import DomainExtensionCreate, DomainExtensionUpdate


def get_by_id(db: Session, extension_id: int) -> DomainExtension | None:
    return db.get(DomainExtension, extension_id)


def get_by_extension(db: Session, extension: str) -> DomainExtension | None:
    """
    Match by the stored, normalised form. Caller is responsible for passing a
    normalised string (the schemas do this on the way in).
    """
    return db.scalar(select(DomainExtension).where(DomainExtension.extension == extension))


def list_extensions(
    db: Session, *, include_inactive: bool = False
) -> list[DomainExtension]:
    query = select(DomainExtension)
    if not include_inactive:
        query = query.where(DomainExtension.is_active.is_(True))
    return list(
        db.scalars(query.order_by(DomainExtension.display_order, DomainExtension.id)).all()
    )


def create(db: Session, data: DomainExtensionCreate) -> DomainExtension:
    row = DomainExtension(**data.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def update(
    db: Session, row: DomainExtension, data: DomainExtensionUpdate
) -> DomainExtension:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(row, field, value)
    db.commit()
    db.refresh(row)
    return row


def deactivate(db: Session, row: DomainExtension) -> DomainExtension:
    row.is_active = False
    db.commit()
    db.refresh(row)
    return row


def match_for_domain_name(db: Session, domain_name: str) -> DomainExtension | None:
    """
    Find the extension the given domain name ends with, or None.

    Longest-match wins -- `.co.rw` beats `.rw`, so a `.co.rw` domain is priced
    off a `.co.rw` row if one exists rather than off `.rw`. All comparisons are
    on the stored lowercase, dot-prefixed form.
    """
    name = (domain_name or "").strip().lower()
    if "." not in name:
        return None
    extensions = list_extensions(db)
    extensions.sort(key=lambda e: len(e.extension), reverse=True)
    for ext in extensions:
        if name.endswith(ext.extension):
            return ext
    return None
