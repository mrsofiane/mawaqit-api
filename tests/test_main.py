from fastapi.testclient import TestClient
import os

from main import app

client = TestClient(app)
API_ROOT = "/api/v1"

AUTH_ENABLED = os.getenv("USE_AUTH", "false").lower() == "true"
BEARER_TOKEN = (
    os.getenv("BEARER_TOKEN", "test-token-for-testing") if AUTH_ENABLED else None
)
HEADERS = (
    {"Authorization": f"Bearer {BEARER_TOKEN}"} if AUTH_ENABLED and BEARER_TOKEN else {}
)


def test_read_root():
    """Root endpoint should be accessible without authentication"""
    response = client.get(API_ROOT)
    assert response.status_code == 200
    assert response.json() == {
        "Greetings": "Hello and Welcome to this Api, this api use the mawaqit.net as data source of prayers time in more than 8000 masjid, this api can be used to fetch data in json, you can find our docs on /docs. "
    }


def test_missing_bearer_token():
    """Requests without bearer token should return 401 only if auth is enabled"""
    response = client.get(f"{API_ROOT}/assalam-argenteuil/prayer-times")
    if AUTH_ENABLED:
        assert response.status_code == 401
        assert (
            "Authorization" in response.json()["detail"]
            or "bearer" in response.json()["detail"].lower()
        )
    else:
        assert response.status_code == 200


def test_invalid_bearer_token():
    """Requests with invalid bearer token should return 401 only if auth is enabled"""
    if not AUTH_ENABLED:
        return

    response = client.get(
        f"{API_ROOT}/assalam-argenteuil/prayer-times",
        headers={"Authorization": "Bearer invalid-token"},
    )
    assert response.status_code == 401


def test_get_prayer_times():
    """Prayer times endpoint"""
    response = client.get(
        f"{API_ROOT}/assalam-argenteuil/prayer-times", headers=HEADERS
    )
    r_json = response.json()
    assert response.status_code == 200
    assert len(r_json) == 6


def test_get_year_calendar():
    """Year calendar endpoint"""
    response = client.get(f"{API_ROOT}/assalam-argenteuil/calendar", headers=HEADERS)
    r_json = response.json()
    assert response.status_code == 200
    assert len(r_json["calendar"]) == 12


def test_get_month_calendar():
    """Month calendar endpoint"""
    response = client.get(f"{API_ROOT}/assalam-argenteuil/calendar/1", headers=HEADERS)
    r_json = response.json()
    assert response.status_code == 200
    assert len(r_json) == 31


def test_get_announcements():
    """Announcements endpoint"""
    response = client.get(
        f"{API_ROOT}/assalam-argenteuil/announcements", headers=HEADERS
    )
    assert response.status_code == 200


def test_get_services():
    """Services endpoint"""
    response = client.get(f"{API_ROOT}/assalam-argenteuil/services", headers=HEADERS)
    assert response.status_code == 200


def test_get_month_calendar_iqama():
    """Month calendar iqama endpoint"""
    response = client.get(
        f"{API_ROOT}/assalam-argenteuil/calendar-iqama/1", headers=HEADERS
    )
    r_json = response.json()
    assert response.status_code == 200
    assert len(r_json) == 31
