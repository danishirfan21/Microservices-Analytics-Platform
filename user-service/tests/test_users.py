import pytest
from fastapi import status

def test_create_user(client):
    """Test user registration"""
    response = client.post(
        "/users/",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123",
            "full_name": "Test User"
        }
    )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert "id" in data
    assert "hashed_password" not in data

def test_create_duplicate_user(client):
    """Test creating duplicate user fails"""
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123"
    }

    # Create first user
    response1 = client.post("/users/", json=user_data)
    assert response1.status_code == status.HTTP_201_CREATED

    # Try to create duplicate
    response2 = client.post("/users/", json=user_data)
    assert response2.status_code == status.HTTP_400_BAD_REQUEST

def test_login(client):
    """Test user login"""
    # Create user
    client.post(
        "/users/",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123"
        }
    )

    # Login
    response = client.post(
        "/login",
        json={
            "username": "testuser",
            "password": "testpass123"
        }
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials(client):
    """Test login with invalid credentials"""
    response = client.post(
        "/login",
        json={
            "username": "nonexistent",
            "password": "wrongpass"
        }
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_get_current_user(client):
    """Test getting current user profile"""
    # Create and login
    client.post(
        "/users/",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123"
        }
    )

    login_response = client.post(
        "/login",
        json={"username": "testuser", "password": "testpass123"}
    )
    token = login_response.json()["access_token"]

    # Get current user
    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["username"] == "testuser"

def test_get_users_unauthorized(client):
    """Test getting users without authentication"""
    response = client.get("/users/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_update_user(client):
    """Test updating user profile"""
    # Create and login
    create_response = client.post(
        "/users/",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123"
        }
    )
    user_id = create_response.json()["id"]

    login_response = client.post(
        "/login",
        json={"username": "testuser", "password": "testpass123"}
    )
    token = login_response.json()["access_token"]

    # Update user
    response = client.put(
        f"/users/{user_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"full_name": "Updated Name"}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["full_name"] == "Updated Name"

def test_delete_user(client):
    """Test deleting user"""
    # Create and login
    create_response = client.post(
        "/users/",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123"
        }
    )
    user_id = create_response.json()["id"]

    login_response = client.post(
        "/login",
        json={"username": "testuser", "password": "testpass123"}
    )
    token = login_response.json()["access_token"]

    # Delete user
    response = client.delete(
        f"/users/{user_id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT

def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "healthy"}
