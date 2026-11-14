from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.schemas.user import UserCreate, UserRead


def test_valid_user_creation():
    """Valid user information should pass validation."""
    user = UserCreate(
        username="testuser",
        email="test@example.com",
        password="SecurePass123!",
    )

    assert user.username == "testuser"
    assert user.email == "test@example.com"


def test_invalid_email():
    """Invalid email addresses should be rejected."""
    with pytest.raises(ValidationError):
        UserCreate(
            username="testuser",
            email="invalid-email",
            password="SecurePass123!",
        )


def test_short_username():
    """Usernames must contain at least three characters."""
    with pytest.raises(ValidationError):
        UserCreate(
            username="ab",
            email="test@example.com",
            password="SecurePass123!",
        )


def test_short_password():
    """Passwords must contain at least eight characters."""
    with pytest.raises(ValidationError):
        UserCreate(
            username="testuser",
            email="test@example.com",
            password="123",
        )


def test_user_read_excludes_password():
    """API responses must not expose passwords or hashes."""
    user = UserRead(
        id=1,
        username="testuser",
        email="test@example.com",
        created_at=datetime.now(timezone.utc),
    )

    result = user.model_dump()

    assert result["username"] == "testuser"
    assert "password" not in result
    assert "password_hash" not in result