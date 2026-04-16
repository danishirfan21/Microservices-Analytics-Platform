import pytest
import httpx
import time
import os

USER_SERVICE_URL = "http://localhost:8000"
ANALYTICS_SERVICE_URL = "http://localhost:8001"

@pytest.mark.asyncio
async def test_user_registration_to_analytics_flow():
    """
    Scenario: User registers in User Service.
    Requirement: User Service should send 'user_registered' event to Analytics Service.
    Verification: Analytics Service reflects the new user and event.
    """
    async with httpx.AsyncClient() as client:
        # 1. Register a new user
        unique_id = int(time.time())
        username = f"e2e_user_{unique_id}"
        reg_response = await client.post(
            f"{USER_SERVICE_URL}/users/",
            json={
                "username": username,
                "email": f"{username}@example.com",
                "password": "password123",
                "full_name": "E2E Test User"
            }
        )
        assert reg_response.status_code == 201
        user_id = reg_response.json()["id"]

        # 2. Give background task some time to propagate event
        time.sleep(2)

        # 3. Verify event in Analytics Service
        events_response = await client.get(f"{ANALYTICS_SERVICE_URL}/analytics/events?user_id={user_id}")
        assert events_response.status_code == 200
        events = events_response.json()
        assert any(e["event_type"] == "user_registered" for e in events)

@pytest.mark.asyncio
async def test_auth_and_activity_flow():
    """
    Scenario: User logs in.
    Requirement: User Service should send 'user_login' event to Analytics Service.
    Verification: Token is valid and event is recorded.
    """
    async with httpx.AsyncClient() as client:
        # Setup: Ensure user exists
        username = f"auth_user_{int(time.time())}"
        await client.post(
            f"{USER_SERVICE_URL}/users/",
            json={"username": username, "email": f"{username}@example.com", "password": "password123"}
        )

        # 1. Login
        login_response = await client.post(
            f"{USER_SERVICE_URL}/login",
            json={"username": username, "password": "password123"}
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]

        # 2. Access protected resource
        me_response = await client.get(
            f"{USER_SERVICE_URL}/users/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert me_response.status_code == 200
        user_id = me_response.json()["id"]

        # 3. Verify 'user_login' event
        time.sleep(2)
        events_response = await client.get(f"{ANALYTICS_SERVICE_URL}/analytics/events?user_id={user_id}&event_type=user_login")
        assert events_response.status_code == 200
        assert len(events_response.json()) >= 1

@pytest.mark.asyncio
async def test_user_service_resilience_when_analytics_down():
    """
    Scenario: Analytics Service is down.
    Requirement: User Service should still allow user registration and login.
    """
    # Note: This test assumes Analytics Service is ALREADY DOWN from previous manual step
    # or it will be skipped/fail if Analytics is up.
    # In a real CI environment, we would explicitly stop the service here.

    # Check if analytics is down
    analytics_up = True
    try:
        async with httpx.AsyncClient() as client:
            await client.get(ANALYTICS_SERVICE_URL, timeout=1.0)
    except:
        analytics_up = False

    if analytics_up:
        pytest.skip("Analytics service is still up, skipping resilience test")

    async with httpx.AsyncClient() as client:
        username = f"resilient_{int(time.time())}"
        response = await client.post(
            f"{USER_SERVICE_URL}/users/",
            json={"username": username, "email": f"{username}@example.com", "password": "password123"}
        )
        assert response.status_code == 201
        assert response.json()["username"] == username

@pytest.mark.asyncio
async def test_invalid_data_error_propagation():
    """
    Scenario: Submit invalid registration data.
    Requirement: System returns 422 Unprocessable Entity.
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{USER_SERVICE_URL}/users/",
            json={"username": "sh", "email": "bad-email", "password": "1"}
        )
        assert response.status_code == 422
