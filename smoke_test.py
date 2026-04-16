import requests
import time
import sys
import logging
from datetime import datetime

# Configuration
USER_SERVICE_URL = "http://localhost:8000"
ANALYTICS_SERVICE_URL = "http://localhost:8001"
MAX_RETRIES = 5
RETRY_DELAY = 2

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("smoke-test")

def retry_request(method, url, **kwargs):
    for i in range(MAX_RETRIES):
        try:
            response = requests.request(method, url, **kwargs)
            if response.status_code < 500:
                return response
            logger.warning(f"Server error {response.status_code} at {url}, retrying...")
        except requests.exceptions.RequestException as e:
            logger.warning(f"Connection error at {url}: {e}, retrying...")
        time.sleep(RETRY_DELAY)
    logger.error(f"Failed to call {url} after {MAX_RETRIES} attempts")
    sys.exit(1)

def run_smoke_test():
    logger.info("Starting smoke test for Microservices Analytics Platform...")

    unique_id = int(time.time())
    username = f"smoke_user_{unique_id}"
    password = "smoke_password_123"
    email = f"{username}@example.com"

    # 1. Register a new user
    logger.info(f"Step 1: Registering new user '{username}'...")
    reg_payload = {
        "username": username,
        "email": email,
        "password": password,
        "full_name": "Smoke Test User"
    }
    response = retry_request("POST", f"{USER_SERVICE_URL}/users/", json=reg_payload)
    if response.status_code != 201:
        logger.error(f"Registration failed: {response.text}")
        sys.exit(1)
    user_data = response.json()
    user_id = user_data["id"]
    logger.info(f"Successfully registered user with ID: {user_id}")

    # 2. Login and get token
    logger.info("Step 2: Logging in to retrieve JWT token...")
    login_payload = {
        "username": username,
        "password": password
    }
    response = retry_request("POST", f"{USER_SERVICE_URL}/login", json=login_payload)
    if response.status_code != 200:
        logger.error(f"Login failed: {response.text}")
        sys.exit(1)
    token = response.json()["access_token"]
    logger.info("Successfully retrieved JWT token")

    # 3. Call protected endpoint
    logger.info("Step 3: Accessing protected '/users/me' endpoint...")
    headers = {"Authorization": f"Bearer {token}"}
    response = retry_request("GET", f"{USER_SERVICE_URL}/users/me", headers=headers)
    if response.status_code != 200:
        logger.error(f"Failed to access protected endpoint: {response.text}")
        sys.exit(1)
    logger.info(f"Verified profile data for: {response.json()['username']}")

    # 4. Create analytics events
    logger.info("Step 4: Manually triggering custom analytics events...")
    event_payload = {
        "event_type": "smoke_test_pulse",
        "user_id": user_id,
        "event_metadata": {"source": "smoke_script", "iteration": 1}
    }
    response = retry_request("POST", f"{ANALYTICS_SERVICE_URL}/analytics/events", json=event_payload)
    if response.status_code != 201:
        logger.error(f"Event creation failed: {response.text}")
        sys.exit(1)
    logger.info("Custom event recorded successfully")

    # Give background tasks and DB a moment
    time.sleep(2)

    # 5. Fetch analytics summary
    logger.info("Step 5: Fetching analytics summary report...")
    response = retry_request("GET", f"{ANALYTICS_SERVICE_URL}/analytics/summary")
    if response.status_code != 200:
        logger.error(f"Failed to fetch summary: {response.text}")
        sys.exit(1)
    summary = response.json()
    logger.info("Successfully fetched analytics summary")

    # 6. Validate expected data
    logger.info("Step 6: Validating summary data integrity...")
    if summary["total_events"] < 1:
        logger.error("Data Validation Error: Expected at least 1 event in summary")
        sys.exit(1)

    if "smoke_test_pulse" not in summary["event_type_counts"]:
        logger.error("Data Validation Error: 'smoke_test_pulse' event type not found in summary")
        sys.exit(1)

    logger.info("Data integrity checks passed")
    logger.info("SMOKE TEST PASSED SUCCESSFULLY")

if __name__ == "__main__":
    try:
        run_smoke_test()
    except Exception as e:
        logger.error(f"Unexpected error during smoke test: {e}")
        sys.exit(1)
