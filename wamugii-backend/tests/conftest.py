import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401  -- register models on Base.metadata
from app.core.database import Base, get_db
from app.core.security import create_access_token
from app.crud import user as user_crud
from app.main import app
from app.models.user import Role
from app.schemas.user import UserCreate

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def _override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = _override_get_db


@pytest.fixture(autouse=True)
def _reset_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)


def _make_auth_headers(role: Role) -> dict:
    db = TestingSessionLocal()
    try:
        user = user_crud.create(
            db,
            UserCreate(
                full_name=f"{role.value} User",
                email=f"{role.value.lower()}@example.com",
                password="password123",
            ),
            role=role,
        )
        token = create_access_token(user.id)
        return {"Authorization": f"Bearer {token}"}
    finally:
        db.close()


@pytest.fixture
def admin_headers():
    return _make_auth_headers(Role.ADMIN)


@pytest.fixture
def staff_headers():
    return _make_auth_headers(Role.STAFF)


@pytest.fixture
def client_headers():
    return _make_auth_headers(Role.CLIENT)
