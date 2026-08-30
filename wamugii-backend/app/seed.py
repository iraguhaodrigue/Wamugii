"""Create the first ADMIN user. Run once: python -m app.seed"""
from app.core.config import settings
from app.core.database import SessionLocal
from app.crud import user as user_crud
from app.models.user import Role
from app.schemas.user import UserCreate


def main() -> None:
    db = SessionLocal()
    try:
        existing = user_crud.get_by_email(db, settings.FIRST_ADMIN_EMAIL.lower())
        if existing:
            print(f"Admin already exists: {existing.email}")
            return
        admin = user_crud.create(
            db,
            UserCreate(
                full_name="WAMUGII Admin",
                email=settings.FIRST_ADMIN_EMAIL,
                password=settings.FIRST_ADMIN_PASSWORD,
            ),
            role=Role.ADMIN,
        )
        print(f"Created admin: {admin.email}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
