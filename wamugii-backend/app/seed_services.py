"""Seed the 9 core services. Safe to run more than once: python -m app.seed_services"""
from app.core.database import SessionLocal
from app.crud import service as service_crud
from app.schemas.service import ServiceCreate

SERVICES = [
    "Web Design & Development",
    "Software Development",
    "Project Development",
    "IT Consultancy",
    "Hosting & Domains",
    "Installation & IT Solutions",
    "Research & Technical Support",
    "Electronics & Technology",
    "Beauty Gadgets & Tools",
]


def main() -> None:
    db = SessionLocal()
    try:
        for name in SERVICES:
            slug = service_crud.slugify(name)
            if service_crud.get_by_slug(db, slug):
                print(f"Service already exists: {name}")
                continue
            service = service_crud.create(db, ServiceCreate(name=name))
            print(f"Created service: {service.name}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
