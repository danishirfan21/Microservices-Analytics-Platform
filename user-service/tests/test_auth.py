import pytest
from app.auth import get_password_hash, verify_password, create_access_token, SECRET_KEY, ALGORITHM
from datetime import timedelta
from fastapi import status
from jose import jwt
import time

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

def test_expired_token(client):
    """
    Scenario: User attempts to authenticate with an expired JWT token.
    Prevents: Unauthorized access via old/compromised tokens.
    """
    data = {"sub": "testuser", "exp": int(time.time()) - 3600}
    token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Could not validate credentials"

def test_token_with_invalid_user(client):
    """
    Scenario: Valid JWT token for a user that no longer exists in the database.
    Prevents: Authentication of deleted users who still hold a valid token.
    """
    data = {"sub": "nonexistentuser"}
    token = create_access_token(data)

    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_inactive_user_token(client, db_session):
    """
    Scenario: User with is_active=False attempts to access protected routes.
    Prevents: Blocked/disabled users from performing actions.
    """
    from app.models import User

    hashed_password = get_password_hash("password123")
    user = User(username="inactive", email="inactive@example.com", hashed_password=hashed_password, is_active=False)
    db_session.add(user)
    db_session.commit()

    token = create_access_token({"sub": "inactive"})

    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Inactive user"
