import base64
import os
import time
import pytest
import requests

API = "https://api.spotify.com/v1"
AUTH = "https://accounts.spotify.com/api/token"
CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
TRACK_ID = os.getenv("SPOTIFY_TRACK_ID", "11dFghVXANMlKmJ8NB4b1k")

@pytest.fixture(scope="session")
def token():
    if not CLIENT_ID or not CLIENT_SECRET:
        pytest.skip("Не заданы SPOTIFY_CLIENT_ID и SPOTIFY_CLIENT_SECRET")
    raw = f"{CLIENT_ID}:{CLIENT_SECRET}".encode()
    encoded = base64.b64encode(raw).decode()
    response = requests.post(
        AUTH,
        headers={"Authorization": f"Basic {encoded}"},
        data={"grant_type": "client_credentials"},
        timeout=20,
    )
    assert response.status_code == 200, f"Ошибка OAuth: {response.status_code} {response.text}"
    data = response.json()
    assert data.get("access_token")
    return data["access_token"]

@pytest.fixture
def api(token):
    session = requests.Session()
    session.headers.update({"Authorization": f"Bearer {token}"})
    return session

def test_search_track_positive(api):
    r = api.get(f"{API}/search", params={"q": "Twenty One Pilots", "type": "track", "limit": 5}, timeout=20)
    assert r.status_code == 200, r.text
    body = r.json()
    assert "tracks" in body and isinstance(body["tracks"]["items"], list)

def test_search_empty_query_negative(api):
    r = api.get(f"{API}/search", params={"q": "", "type": "track"}, timeout=20)
    assert r.status_code in (400, 200), r.text
    if r.status_code == 200:
        assert isinstance(r.json().get("tracks", {}).get("items", []), list)

def test_search_no_results(api):
    r = api.get(f"{API}/search", params={"q": "xyzqwerty123notarealtrack", "type": "track"}, timeout=20)
    assert r.status_code == 200, r.text
    assert isinstance(r.json()["tracks"]["items"], list)
    assert len(r.json()["tracks"]["items"]) == 0

def test_get_track_positive(api):
    r = api.get(f"{API}/tracks/{TRACK_ID}", timeout=20)
    assert r.status_code == 200, r.text
    body = r.json()
    for key in ("id", "name", "artists", "album", "duration_ms"):
        assert key in body
    assert isinstance(body["artists"], list)

def test_get_track_invalid_id(api):
    r = api.get(f"{API}/tracks/invalid_track_id_123", timeout=20)
    assert r.status_code in (400, 404), r.text

def test_me_without_token():
    r = requests.get(f"{API}/me", timeout=20)
    assert r.status_code == 401, r.text

def test_me_with_invalid_token():
    r = requests.get(f"{API}/me", headers={"Authorization": "Bearer invalid-token"}, timeout=20)
    assert r.status_code == 401, r.text

def test_delete_search_unsupported_method(api):
    r = api.delete(f"{API}/search", timeout=20)
    assert r.status_code in (400, 401, 403, 404, 405), r.text

def test_nonexistent_endpoint(api):
    r = api.get(f"{API}/nonexistent_endpoint_lab4", timeout=20)
    assert r.status_code in (404, 410), r.text

def test_track_response_contract(api):
    r = api.get(f"{API}/tracks/{TRACK_ID}", timeout=20)
    assert r.status_code == 200, r.text
    body = r.json()
    assert isinstance(body["id"], str) and body["id"]
    assert isinstance(body["name"], str)
    assert isinstance(body["artists"], list)
    assert isinstance(body["album"], dict)
    assert isinstance(body["duration_ms"], int) and body["duration_ms"] >= 0

def test_search_boundary_limit(api):
    r = api.get(f"{API}/search", params={"q": "test", "type": "track", "limit": 0}, timeout=20)
    assert r.status_code in (200, 400), r.text
