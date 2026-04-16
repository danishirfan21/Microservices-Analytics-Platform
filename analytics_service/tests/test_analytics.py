import pytest
from fastapi import status
from datetime import datetime, timedelta, timezone
import unittest.mock as mock

def test_create_event(client):
    """Test creating an analytics event"""
    response = client.post(
        "/analytics/events",
        json={
            "event_type": "user_login",
            "user_id": 1,
            "event_metadata": {"ip": "127.0.0.1"}
        }
    )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["event_type"] == "user_login"
    assert data["user_id"] == 1
    assert "id" in data
    assert "created_at" in data

def test_get_events(client):
    """Test retrieving events"""
    # Create some events
    for i in range(3):
        client.post(
            "/analytics/events",
            json={
                "event_type": f"test_event_{i}",
                "user_id": i + 1,
                "event_metadata": {}
            }
        )

    # Get all events
    response = client.get("/analytics/events")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 3

def test_get_events_with_filter(client):
    """Test retrieving events with filters"""
    # Create events
    client.post(
        "/analytics/events",
        json={"event_type": "user_login", "user_id": 1, "event_metadata": {}}
    )
    client.post(
        "/analytics/events",
        json={"event_type": "user_logout", "user_id": 1, "event_metadata": {}}
    )
    client.post(
        "/analytics/events",
        json={"event_type": "user_login", "user_id": 2, "event_metadata": {}}
    )

    # Filter by event type
    response = client.get("/analytics/events?event_type=user_login")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2

    # Filter by user_id
    response = client.get("/analytics/events?user_id=1")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2

def test_get_analytics_summary(client):
    """Test getting analytics summary"""
    # Create test events
    client.post(
        "/analytics/events",
        json={"event_type": "user_login", "user_id": 1, "event_metadata": {}}
    )
    client.post(
        "/analytics/events",
        json={"event_type": "user_login", "user_id": 2, "event_metadata": {}}
    )
    client.post(
        "/analytics/events",
        json={"event_type": "profile_updated", "user_id": 1, "event_metadata": {}}
    )

    # Get summary
    response = client.get("/analytics/summary")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "total_users" in data
    assert "active_users_24h" in data
    assert "total_events" in data
    assert "event_type_counts" in data
    assert data["total_events"] == 3
    assert data["event_type_counts"]["user_login"] == 2
    assert data["event_type_counts"]["profile_updated"] == 1

def test_get_events_by_type(client):
    """Test getting event counts by type"""
    # Create events
    for i in range(3):
        client.post(
            "/analytics/events",
            json={"event_type": "user_login", "user_id": i + 1, "event_metadata": {}}
        )
    for i in range(2):
        client.post(
            "/analytics/events",
            json={"event_type": "profile_updated", "user_id": i + 1, "event_metadata": {}}
        )

    # Get events by type
    response = client.get("/analytics/events/by-type")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2
    assert data[0]["event_type"] == "user_login"
    assert data[0]["count"] == 3
    assert data[1]["event_type"] == "profile_updated"
    assert data[1]["count"] == 2

def test_get_analytics_by_date_range(client):
    """Test getting analytics for a date range"""
    # Create events
    client.post(
        "/analytics/events",
        json={"event_type": "user_login", "user_id": 1, "event_metadata": {}}
    )
    client.post(
        "/analytics/events",
        json={"event_type": "user_login", "user_id": 2, "event_metadata": {}}
    )

    # Get date range analytics (default last 7 days)
    response = client.get("/analytics/events/date-range")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "total_events" in data
    assert "unique_users" in data
    assert "event_breakdown" in data
    assert data["total_events"] == 2
    assert data["unique_users"] == 2

def test_get_user_events(client):
    """Test getting events for specific user"""
    # Create events for different users
    for i in range(3):
        client.post(
            "/analytics/events",
            json={"event_type": "test_event", "user_id": 1, "event_metadata": {}}
        )
    client.post(
        "/analytics/events",
        json={"event_type": "test_event", "user_id": 2, "event_metadata": {}}
    )

    # Get events for user 1
    response = client.get("/analytics/users/1/events")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 3
    for event in data:
        assert event["user_id"] == 1

def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "healthy"}

def test_event_pagination(client):
    """Test event pagination"""
    # Create 15 events
    for i in range(15):
        client.post(
            "/analytics/events",
            json={"event_type": "test_event", "user_id": 1, "event_metadata": {}}
        )

    # Get first page
    response = client.get("/analytics/events?skip=0&limit=10")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 10

    # Get second page
    response = client.get("/analytics/events?skip=10&limit=10")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 5

def test_create_event_invalid_data(client):
    """
    Scenario: Attempt to create an event with missing user_id or event_type.
    Prevents: Recording of incomplete or malformed events.
    """
    # Missing event_type
    response = client.post(
        "/analytics/events",
        json={"user_id": 1, "event_metadata": {}}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # Missing user_id
    response = client.post(
        "/analytics/events",
        json={"event_type": "test_event", "event_metadata": {}}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_get_analytics_by_specific_date_range(client):
    """
    Scenario: Request analytics summary for a specific date range.
    Prevents: Incorrect aggregations when filtering by date.
    """
    # Create an event
    client.post(
        "/analytics/events",
        json={"event_type": "user_login", "user_id": 1, "event_metadata": {}}
    )

    # Using simple ISO format without timezone for test simplicity
    now = datetime.now()
    start_date = (now - timedelta(days=1)).isoformat()
    end_date = (now + timedelta(days=1)).isoformat()

    response = client.get(f"/analytics/events/date-range?start_date={start_date}&end_date={end_date}")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total_events"] >= 1

@mock.patch("httpx.AsyncClient.get")
def test_create_event_user_service_down(mock_get, client):
    """
    Scenario: User validation fails because User Service is down during event creation.
    Prevents: Event recording being blocked by external service failures.
    """
    mock_get.side_effect = Exception("User Service down")

    response = client.post(
        "/analytics/events",
        json={
            "event_type": "resilient_event",
            "user_id": 999,
            "event_metadata": {}
        }
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["event_type"] == "resilient_event"

@mock.patch("httpx.AsyncClient.get")
def test_summary_user_service_down_fallback(mock_get, client):
    """
    Scenario: Analytics summary is requested, but User Service is down.
    Prevents: Summary calculation failure by falling back to local data (counting distinct user_ids from events).
    """
    mock_get.side_effect = Exception("User Service down")

    # Create an event to have some data for fallback
    client.post(
        "/analytics/events",
        json={"event_type": "test", "user_id": 1, "event_metadata": {}}
    )

    response = client.get("/analytics/summary")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    # Should fallback to counting distinct users from events
    assert data["total_users"] == 1

def test_date_range_boundaries(client):
    """
    Scenario: Request date range that includes no events.
    Prevents: Errors or null values when aggregations return empty sets.
    """
    now = datetime.now()
    future_date = (now + timedelta(days=100)).isoformat()

    response = client.get(f"/analytics/events/date-range?start_date={future_date}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["total_events"] == 0

@mock.patch("sqlalchemy.orm.Session.commit")
def test_analytics_database_failure(mock_commit, client):
    """
    Scenario: Database is unavailable during event creation in Analytics Service.
    Prevents: System crashing or returning unhandled exceptions when recording events.
    """
    mock_commit.side_effect = Exception("Analytics DB connection lost")

    from fastapi.testclient import TestClient
    from analytics_service.analytics_app.main import app

    with TestClient(app, raise_server_exceptions=False) as no_raise_client:
        response = no_raise_client.post(
            "/analytics/events",
            json={
                "event_type": "db_fail_event",
                "user_id": 1,
                "event_metadata": {}
            }
        )
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
