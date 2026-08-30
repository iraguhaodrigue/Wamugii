from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models.user import Role, User
from app.schemas.user import UserAdminUpdate, UserCreate


def get_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email))


def get_by_id(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)


def create(db: Session, data: UserCreate, role: Role = Role.CLIENT) -> User:
    user = User(
        full_name=data.full_name,
        email=data.email.lower(),
        phone=data.phone,
        password_hash=hash_password(data.password),
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate(db: Session, email: str, password: str) -> User | None:
    user = get_by_email(db, email.lower())
    if not user or not verify_password(password, user.password_hash):
        return None
    return user


def count_all(db: Session) -> int:
    return db.scalar(select(func.count()).select_from(User)) or 0


def count_by_role(db: Session, role: Role) -> int:
    return db.scalar(select(func.count()).select_from(User).where(User.role == role)) or 0


def count_active_admins(db: Session) -> int:
    return (
        db.scalar(
            select(func.count())
            .select_from(User)
            .where(User.role == Role.ADMIN, User.is_active.is_(True))
        )
        or 0
    )


def list_admin(
    db: Session,
    *,
    limit: int = 20,
    offset: int = 0,
    search: str | None = None,
    role: Role | None = None,
) -> list[User]:
    query = select(User)
    if role is not None:
        query = query.where(User.role == role)
    if search:
        term = search.lower()
        query = query.where(
            func.lower(User.full_name).contains(term) | func.lower(User.email).contains(term)
        )
    query = query.order_by(User.id).offset(offset).limit(limit)
    return list(db.scalars(query).all())


def update_admin_fields(db: Session, user: User, data: UserAdminUpdate) -> User:
    updates = data.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user


def deactivate(db: Session, user: User) -> User:
    user.is_active = False
    db.commit()
    db.refresh(user)
    return user
