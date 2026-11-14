from app.core.security import hash_password, verify_password


def test_password_is_hashed():
    """Passwords must not be stored as plaintext."""
    password = "SecureTest123!"
    hashed = hash_password(password)

    assert hashed != password
    assert hashed.startswith("$2b$")


def test_correct_password():
    """A correct password must match its stored hash."""
    password = "SecureTest123!"
    hashed = hash_password(password)

    assert verify_password(password, hashed) is True


def test_incorrect_password():
    """An incorrect password must be rejected."""
    hashed = hash_password("SecureTest123!")

    assert verify_password("WrongPassword123!", hashed) is False


def test_unique_salts():
    """Hashing the same password twice must produce different hashes."""
    password = "SecureTest123!"

    first_hash = hash_password(password)
    second_hash = hash_password(password)

    assert first_hash != second_hash
    assert verify_password(password, first_hash)
    assert verify_password(password, second_hash)
