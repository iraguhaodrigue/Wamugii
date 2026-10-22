"""
SAMPLE starter domain extensions for a fresh install.

    python -m app.seed_domain_extensions

The migration that creates the table already inserts the same rows idempotently,
so a normal `alembic upgrade head` leaves nothing for this script to do. It is
kept for parity with the other seed scripts and as the way to top up on an
install where the admin has since removed some of the defaults by hand -- the
same safety rules apply:

* Match on the normalised extension string (`.com`, lowercased, dot-prefixed).
* Insert only when there is no existing row for that extension (active or
  soft-deleted). A deliberate removal is never resurrected.
* Never overwrite an admin's cost or margin.

The numbers are placeholders. Replace them against the real registrar invoices
through the admin Extensions screen -- editing a cost or the margin updates the
computed client price everywhere by the next read.
"""

from decimal import Decimal

from app.core.database import SessionLocal
from app.crud import domain_extension as extension_crud
from app.schemas.domain_extension import DomainExtensionCreate

SEED_EXTENSIONS: list[DomainExtensionCreate] = [
    DomainExtensionCreate(extension=".com", cost_price=Decimal("16000.00"), display_order=1),
    DomainExtensionCreate(extension=".rw",  cost_price=Decimal("14000.00"), display_order=2),
    DomainExtensionCreate(extension=".org", cost_price=Decimal("17000.00"), display_order=3),
    DomainExtensionCreate(extension=".net", cost_price=Decimal("18000.00"), display_order=4),
    DomainExtensionCreate(extension=".io",  cost_price=Decimal("60000.00"), display_order=5),
    DomainExtensionCreate(extension=".co",  cost_price=Decimal("35000.00"), display_order=6),
]


def main() -> None:
    db = SessionLocal()
    try:
        for payload in SEED_EXTENSIONS:
            # Normalisation already happened via the schema validator.
            existing = extension_crud.get_by_extension(db, payload.extension)
            if existing is not None:
                print(f"  already present: {payload.extension}")
                continue
            created = extension_crud.create(db, payload)
            print(
                f"  created {created.extension}: cost {created.cost_price}, "
                f"margin {created.margin}, client price {created.client_price}"
            )
    finally:
        db.close()


if __name__ == "__main__":
    main()
