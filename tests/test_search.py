from fastapi.testclient import TestClient

from main import app
from config.settings import settings
import scraping.search as search

client = TestClient(app)
SEARCH_URL = "/api/v1/search"

SEARXNG_RESULTS = {
    "results": [
        {"url": "https://mawaqit.net/fr/assalam-argenteuil", "title": "Mosquée Assalam - Argenteuil - Mawaqit"},
        {"url": "https://mawaqit.net/en/m/assalam-argenteuil", "title": "Mosquée Assalam (mobile)"},
        {"url": "https://mawaqit.net/en/blog/some-article", "title": "Blog post | Mawaqit"},
        {"url": "https://mawaqit.net/en/", "title": "Mawaqit"},
        {"url": "https://example.com/fr/assalam-argenteuil", "title": "Not mawaqit"},
        {"url": "https://mawaqit.net/nl/w/al-fourkaan-eindhoven", "title": "Al Fourkaan | Mawaqit"},
    ]
}


class FakeResponse:
    def __init__(self, status_code=200, payload=None):
        self.status_code = status_code
        self._payload = payload or {}

    def json(self):
        return self._payload


def _setup(monkeypatch, searxng_url="http://searxng:8080", response=None):
    monkeypatch.setattr(settings, "ENABLE_AUTH", False, raising=False)
    monkeypatch.setattr(settings, "SEARXNG_URL", searxng_url, raising=False)
    calls = []

    def fake_get(url, params=None, timeout=None):
        calls.append({"url": url, "params": params})
        return response or FakeResponse(payload=SEARXNG_RESULTS)

    monkeypatch.setattr(search.requests, "get", fake_get)
    return calls


def test_extract_slug():
    assert search.extract_slug("https://mawaqit.net/fr/assalam-argenteuil") == "assalam-argenteuil"
    assert search.extract_slug("https://mawaqit.net/en/m/assalam-argenteuil?view=1") == "assalam-argenteuil"
    assert search.extract_slug("https://mawaqit.net/nl/w/al-fourkaan-eindhoven/") == "al-fourkaan-eindhoven"
    assert search.extract_slug("https://mawaqit.net/en/blog/some-article") is None
    assert search.extract_slug("https://mawaqit.net/en/backoffice") is None
    assert search.extract_slug("https://mawaqit.net/en/") is None
    assert search.extract_slug("https://example.com/fr/assalam-argenteuil") is None


def test_clean_title():
    assert search.clean_title("Mosquée Assalam - Argenteuil - Mawaqit") == "Mosquée Assalam - Argenteuil"
    assert search.clean_title("Al Fourkaan | Mawaqit") == "Al Fourkaan"
    assert search.clean_title("Mawaqit") == "Mawaqit"


def test_search_returns_unique_mosques(monkeypatch):
    calls = _setup(monkeypatch)
    response = client.get(SEARCH_URL, params={"q": "assalam"})
    assert response.status_code == 200
    assert response.json() == [
        {
            "slug": "assalam-argenteuil",
            "name": "Mosquée Assalam - Argenteuil",
            "url": "https://mawaqit.net/fr/assalam-argenteuil",
        },
        {
            "slug": "al-fourkaan-eindhoven",
            "name": "Al Fourkaan",
            "url": "https://mawaqit.net/fr/al-fourkaan-eindhoven",
        },
    ]
    assert calls[0]["url"] == "http://searxng:8080/search"
    assert calls[0]["params"] == {"q": "site:mawaqit.net assalam", "format": "json"}


def test_search_limit(monkeypatch):
    _setup(monkeypatch)
    response = client.get(SEARCH_URL, params={"q": "assalam", "limit": 1})
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_search_disabled_without_searxng_url(monkeypatch):
    _setup(monkeypatch, searxng_url=None)
    response = client.get(SEARCH_URL, params={"q": "assalam"})
    assert response.status_code == 503


def test_search_searxng_error(monkeypatch):
    _setup(monkeypatch, response=FakeResponse(status_code=403))
    response = client.get(SEARCH_URL, params={"q": "assalam"})
    assert response.status_code == 502


def test_search_requires_query(monkeypatch):
    _setup(monkeypatch)
    assert client.get(SEARCH_URL).status_code == 422


def test_search_requires_token_when_auth_enabled(monkeypatch):
    _setup(monkeypatch)
    monkeypatch.setattr(settings, "ENABLE_AUTH", True, raising=False)
    monkeypatch.setattr(settings, "BEARER_TOKEN", "test-secret", raising=False)
    assert client.get(SEARCH_URL, params={"q": "assalam"}).status_code == 401
    response = client.get(SEARCH_URL, params={"q": "assalam"}, headers={"Authorization": "Bearer test-secret"})
    assert response.status_code == 200
