import pytest
import httpx
import time
import os

USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://localhost:8000")
ANALYTICS_SERVICE_URL = os.getenv("ANALYTICS_SERVICE_URL", "http://localhost:8001")

@pytest.mark.asyncio
async def test_full_user_and_analytics_lifecycle():
    """
    Scenario: User registers, logs in, and updates their profile.
    Verification: Analytics Service reflects all events.
    """
    async with httpx.AsyncClient() as client:
        unique_suffix = int(time.time())
        username = f"lifecycle_user_{unique_suffix}"
        password = "securepassword"

        # 1. Register
        reg_resp = await client.post(
            f"{USER_SERVICE_URL}/users/",
            json={"username": username, "email": f"{username}@test.com", "password": password}
        )
        assert reg_resp.status_code == 201
        user_id = reg_resp.json()["id"]

        # 2. Login
        login_resp = await client.post(
            f"{USER_SERVICE_URL}/login",
            json={"username": username, "password": password}
        )
        assert login_resp.status_code == 200
        token = login_resp.json()["access_token"]

        # 3. Update Profile
        update_resp = await client.put(
            f"{USER_SERVICE_URL}/users/{user_id}",
            headers={"Authorization": f"Bearer {token}"},
            json={"full_name": "Integrated Tester"}
        )
        assert update_resp.status_code == 200

        # Give background tasks time to complete
        time.sleep(3)

        # 4. Verify Events in Analytics
        events_resp = await client.get(f"{ANALYTICS_SERVICE_URL}/analytics/events?user_id={user_id}")
        assert events_resp.status_code == 200
        events = [e["event_type"] for e in events_resp.json()]

        assert "user_registered" in events
        assert "user_login" in events
        assert "profile_updated" in events

@pytest.mark.asyncio
async def test_analytics_summary_cross_service_aggregation():
    """
    Scenario: Analytics Service requests total user count from User Service.
    Verification: Summary user count matches User Service count.
    """
    async with httpx.AsyncClient() as client:
        # Get count from User Service
        user_count_resp = await client.get(f"{USER_SERVICE_URL}/users/count")
        assert user_count_resp.status_code == 200
        expected_count = user_count_resp.json()["count"]

        # Get summary from Analytics Service
        summary_resp = await client.get(f"{ANALYTICS_SERVICE_URL}/analytics/summary")
        assert summary_resp.status_code == 200
        actual_count = summary_resp.json()["total_users"]

        assert actual_count == expected_count

@pytest.mark.asyncio
async def test_cross_service_invalid_user_id():
    """
    Goal: Verify Analytics handles received events for non-existent users gracefully.
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{ANALYTICS_SERVICE_URL}/analytics/events",
            json={"event_type": "ghost_action", "user_id": 99999, "event_metadata": {}}
        )
        assert response.status_code == 201
