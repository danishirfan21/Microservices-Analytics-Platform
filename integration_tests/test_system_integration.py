import pytest
import httpx
import time
import subprocess
import os

USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://localhost:8000")
ANALYTICS_SERVICE_URL = os.getenv("ANALYTICS_SERVICE_URL", "http://localhost:8001")

@pytest.mark.asyncio
async def test_full_user_and_analytics_lifecycle():
    """
    Scenario: User registers, logs in, and updates their profile in a real running system.
    Prevents: Breakage in the critical path where User Service fails to trigger events in Analytics Service.
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
    Scenario: Analytics Service requests the total user count from the User Service to build a summary.
    Prevents: Data inconsistency where the dashboard shows incorrect user counts because service-to-service calls fail.
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
async def test_user_service_resilience_to_analytics_outage():
    """
    Scenario: User Service attempts to record an event but the Analytics Service is completely offline.
    Prevents: Cascading failures where the entire system goes down because a non-critical analytics service is unreachable.
    """
    # 1. Stop Analytics Service
    subprocess.run(["pkill", "-f", "uvicorn.*8001"], shell=False)
    time.sleep(1)

    async with httpx.AsyncClient() as client:
        # 2. Attempt Registration
        username = f"resilient_user_{int(time.time())}"
        reg_resp = await client.post(
            f"{USER_SERVICE_URL}/users/",
            json={"username": username, "email": f"{username}@test.com", "password": "password"}
        )
        # Should still succeed despite failing to send event to analytics
        assert reg_resp.status_code == 201

    # 3. Restart Analytics Service for other tests or future runs
    # This uses the environment and paths verified during investigation
    subprocess.Popen(
        "export DATABASE_URL=sqlite:///./test_analytics.db && export USER_SERVICE_URL=http://localhost:8000 && cd /app/analytics-service && uvicorn app.main:app --host 0.0.0.0 --port 8001 > /app/analytics_service.log 2>&1",
        shell=True
    )
    time.sleep(5)

@pytest.mark.asyncio
async def test_invalid_registration_data_validation():
    """
    Scenario: User sends invalid data (short username, bad email) to the registration endpoint.
    Prevents: 500 Internal Server Errors or database corruption from malformed input.
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{USER_SERVICE_URL}/users/",
            json={"username": "a", "email": "not-an-email", "password": "1"}
        )
        assert response.status_code == 422
