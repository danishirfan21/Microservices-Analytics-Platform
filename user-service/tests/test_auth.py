import pytest
from app.auth import get_password_hash, verify_password, create_access_token
from datetime import timedelta

def test_password_hashing():
    """Test password hashing and verification"""
    password = "testpassword123"
    hashed = get_password_hash(password)

    # Hash should be different from plain password
    assert hashed != password

    # Verify correct password
    assert verify_password(password, hashed) is True

    # Verify incorrect password
    assert verify_password("wrongpassword", hashed) is False

def test_create_access_token():
    """Test JWT token creation"""
    data = {"sub": "testuser"}
    token = create_access_token(data)

    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 0

def test_create_access_token_with_expiration():
    """Test JWT token creation with custom expiration"""
    data = {"sub": "testuser"}
    expires_delta = timedelta(minutes=15)
    token = create_access_token(data, expires_delta)

    assert token is not None
    assert isinstance(token, str)
