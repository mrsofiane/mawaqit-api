from hashlib import sha256

from fastapi.testclient import TestClient

from main import app
from config.settings import settings

client = TestClient(app)
API_ROOT = "/api/v1"


def _apply_settings(monkeypatch, enable_auth=False, bearer_token=None):
    """
    Hilfsfunktion: patched settings für Tests.
    """
    monkeypatch.setattr(settings, "ENABLE_AUTH", enable_auth, raising=False)
    monkeypatch.setattr(settings, "BEARER_TOKEN", bearer_token, raising=False)


def _auth_header():
    return (
        {"Authorization": f"Bearer {settings.BEARER_TOKEN}"}
        if getattr(settings, "ENABLE_AUTH", False) and getattr(settings, "BEARER_TOKEN", None)
        else {}
    )


def test_read_root():
    """Root endpoint should be accessible without authentication"""
    response = client.get(API_ROOT)
    assert response.status_code == 200
    assert response.json() == {
        "Greetings": "Hello and Welcome to this Api, this api use the mawaqit.net as data source of prayers time in more than 8000 masjid, this api can be used to fetch data in json, you can find our docs on /docs. "
    }


def test_missing_bearer_token_when_auth_enabled(monkeypatch):
    """Wenn Auth aktiviert ist, sollten Anfragen ohne Token 401 zurückgeben"""
    _apply_settings(monkeypatch, enable_auth=True, bearer_token="test-secret")
    response = client.get(f"{API_ROOT}/assalam-argenteuil/prayer-times")
    assert response.status_code == 401
    detail = response.json().get("detail", "")
    assert "Authorization" in detail or "bearer" in str(detail).lower()


def test_missing_bearer_token_when_auth_disabled(monkeypatch):
    """Wenn Auth deaktiviert ist, sollten Anfragen ohne Token 200 zurückgeben"""
    _apply_settings(monkeypatch, enable_auth=False, bearer_token=None)
    response = client.get(f"{API_ROOT}/assalam-argenteuil/prayer-times")
    assert response.status_code == 200


def test_invalid_bearer_token(monkeypatch):
    """Ungültiges Token sollte 401 zurückgeben, wenn Auth aktiviert ist"""
    _apply_settings(monkeypatch, enable_auth=True, bearer_token="valid-token")
    response = client.get(
        f"{API_ROOT}/assalam-argenteuil/prayer-times",
        headers={"Authorization": "Bearer invalid-token"},
    )
    assert response.status_code == 401


def test_get_prayer_times(monkeypatch):
    """Prayer times endpoint"""
    _apply_settings(monkeypatch, enable_auth=True, bearer_token="valid-token")
    response = client.get(f"{API_ROOT}/assalam-argenteuil/prayer-times", headers=_auth_header())
    r_json = response.json()
    assert response.status_code == 200
    assert len(r_json) == 6


def test_get_year_calendar(monkeypatch):
    """Year calendar endpoint"""
    _apply_settings(monkeypatch, enable_auth=True, bearer_token="valid-token")
    response = client.get(f"{API_ROOT}/assalam-argenteuil/calendar", headers=_auth_header())
    r_json = response.json()
    assert response.status_code == 200
    assert len(r_json["calendar"]) == 12


def test_get_month_calendar(monkeypatch):
    """Month calendar endpoint"""
    _apply_settings(monkeypatch, enable_auth=True, bearer_token="valid-token")
    response = client.get(f"{API_ROOT}/assalam-argenteuil/calendar/1", headers=_auth_header())
    r_json = response.json()
    assert response.status_code == 200
    assert len(r_json) == 31


def test_get_announcements(monkeypatch):
    """Announcements endpoint"""
    _apply_settings(monkeypatch, enable_auth=True, bearer_token="valid-token")
    response = client.get(f"{API_ROOT}/assalam-argenteuil/announcements", headers=_auth_header())
    assert response.status_code == 200


def test_get_services(monkeypatch):
    """Services endpoint"""
    _apply_settings(monkeypatch, enable_auth=True, bearer_token="valid-token")
    response = client.get(f"{API_ROOT}/assalam-argenteuil/services", headers=_auth_header())
    assert response.status_code == 200


def test_get_month_calendar_iqama(monkeypatch):
    """Month calendar iqama endpoint"""
    _apply_settings(monkeypatch, enable_auth=True, bearer_token="valid-token")
    response = client.get(f"{API_ROOT}/assalam-argenteuil/calendar-iqama/1", headers=_auth_header())
    r_json = response.json()
    assert response.status_code == 200
    assert len(r_json) == 31


def test_calendar_ics_headers_and_body(monkeypatch):
    _apply_settings(monkeypatch, enable_auth=False)
    response = client.get(f"{API_ROOT}/assalam-argenteuil/calendar.ics")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/calendar")
    assert 'inline; filename="assalam-argenteuil.ics"' in response.headers["content-disposition"]
    assert response.headers["cache-control"] == "public, max-age=3600"
    body = response.text
    assert body.startswith("BEGIN:VCALENDAR")
    assert "BEGIN:VEVENT" in body
    expected_etag = f'"{sha256(body.encode("utf-8")).hexdigest()}"'
    assert response.headers["etag"] == expected_etag


def test_calendar_iqama_ics(monkeypatch):
    _apply_settings(monkeypatch, enable_auth=False)
    response = client.get(f"{API_ROOT}/assalam-argenteuil/calendar-iqama.ics")
    assert response.status_code == 200
    assert "Iqama" in response.text
    assert "shuruk" not in response.text


def test_calendar_ics_requires_auth_or_query_token(monkeypatch):
    _apply_settings(monkeypatch, enable_auth=True, bearer_token="secret-token")
    denied = client.get(f"{API_ROOT}/assalam-argenteuil/calendar.ics")
    assert denied.status_code == 401

    via_query = client.get(f"{API_ROOT}/assalam-argenteuil/calendar.ics?token=secret-token")
    assert via_query.status_code == 200
    assert via_query.text.startswith("BEGIN:VCALENDAR")

    via_header = client.get(
        f"{API_ROOT}/assalam-argenteuil/calendar.ics",
        headers={"Authorization": "Bearer secret-token"},
    )
    assert via_header.status_code == 200


def test_calendar_ics_duration_validation(monkeypatch):
    _apply_settings(monkeypatch, enable_auth=False)
    assert client.get(f"{API_ROOT}/assalam-argenteuil/calendar.ics?duration=0").status_code == 422
    assert client.get(f"{API_ROOT}/assalam-argenteuil/calendar.ics?duration=181").status_code == 422
    ok = client.get(f"{API_ROOT}/assalam-argenteuil/calendar.ics?duration=10&include_shuruk=true")
    assert ok.status_code == 200
    assert "Shuruk" in ok.text
