from fastapi.testclient import TestClient

from main import app

client = TestClient(app)
API_ROOT= "/api/v1"


def test_read_root():
    response = client.get(API_ROOT)
    assert response.status_code == 200
    assert response.json() == {
        "Greetings": "Hello and Welcome to this Api, this api use the mawaqit.net as data source of prayers time in more than 8000 masjid, this api can be used to fetch data in json, you can find our docs on /docs. "}


def test_get_prayer_times():
    response = client.get(f"{API_ROOT}/assalam-argenteuil/prayer-times")
    r_json = response.json()
    assert response.status_code == 200
    assert len(r_json) == 6

def test_get_year_calendar():
    response = client.get(f"{API_ROOT}/assalam-argenteuil/calendar")
    r_json = response.json()
    assert response.status_code == 200
    assert len(r_json["calendar"]) == 12

def test_get_month_calendar():
    response = client.get(f"{API_ROOT}/assalam-argenteuil/calendar/1")
    r_json = response.json()
    assert response.status_code == 200
    assert len(r_json) == 31