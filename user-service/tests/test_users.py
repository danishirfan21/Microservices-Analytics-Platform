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

def test_update_other_user_forbidden(client):
    """Test updating another user's profile fails"""
    # Create first user
    client.post(
        "/users/",
        json={"username": "user1", "email": "user1@example.com", "password": "password123"}
    )

    # Create second user and login
    create_response2 = client.post(
        "/users/",
        json={"username": "user2", "email": "user2@example.com", "password": "password123"}
    )
    user2_id = create_response2.json()["id"]

    login_response = client.post(
        "/login",
        json={"username": "user1", "password": "password123"}
    )
    token1 = login_response.json()["access_token"]

    # Try to update user 2 with user 1's token
    response = client.put(
        f"/users/{user2_id}",
        headers={"Authorization": f"Bearer {token1}"},
        json={"full_name": "Should Fail"}
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_create_user_invalid_data(client):
    """Test creating user with invalid data fails"""
    # Username too short
    response = client.post(
        "/users/",
        json={"username": "us", "email": "test@example.com", "password": "password123"}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # Password too short
    response = client.post(
        "/users/",
        json={"username": "testuser", "email": "test@example.com", "password": "pass"}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # Invalid email
    response = client.post(
        "/users/",
        json={"username": "testuser", "email": "invalid-email", "password": "password123"}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
