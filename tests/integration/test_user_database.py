import uuid

import pytest
from sqlalchemy.exc import IntegrityError

from app.core.security import hash_password, verify_password
from app.db.database import SessionLocal
from app.db.database import engine
from app.models.user import Base, User


@pytest.fixture(scope="session", autouse=True)
def create_test_tables():
    """Create the users table when testing against a fresh database."""
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture
def db_session():
    """Use a transaction that is rolled back after each test."""
    session = SessionLocal()

    try:
        yield session
    finally:
        session.rollback()
        session.close()


def test_create_user(db_session):
    """A user can be saved with a hashed password."""
    unique_id = uuid.uuid4().hex[:12]
    password = "SecureTest123!"

    user = User(
        username=f"user_{unique_id}",
        email=f"user_{unique_id}@example.com",
        password_hash=hash_password(password),
    )

    db_session.add(user)
    db_session.flush()

    assert user.id is not None
    assert user.password_hash != password
    assert verify_password(password, user.password_hash)


def test_duplicate_username_rejected(db_session):
    """PostgreSQL must reject duplicate usernames."""
    unique_id = uuid.uuid4().hex[:12]
    username = f"user_{unique_id}"

    first = User(
        username=username,
        email=f"first_{unique_id}@example.com",
        password_hash=hash_password("SecureTest123!"),
    )

    second = User(
        username=username,
        email=f"second_{unique_id}@example.com",
        password_hash=hash_password("SecureTest123!"),
    )

    db_session.add(first)
    db_session.flush()

    db_session.add(second)

    with pytest.raises(IntegrityError):
        db_session.flush()


def test_duplicate_email_rejected(db_session):
    """PostgreSQL must reject duplicate email addresses."""
    unique_id = uuid.uuid4().hex[:12]
    email = f"user_{unique_id}@example.com"

    first = User(
        username=f"first_{unique_id}",
        email=email,
        password_hash=hash_password("SecureTest123!"),
    )

    second = User(
        username=f"second_{unique_id}",
        email=email,
        password_hash=hash_password("SecureTest123!"),
    )

    db_session.add(first)
    db_session.flush()

    db_session.add(second)

    with pytest.raises(IntegrityError):
        db_session.flush()
