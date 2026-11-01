
import base64
import os

import pytest
import requests


# Адреса Spotify API
API = "https://api.spotify.com/v1"
AUTH = "https://accounts.spotify.com/api/token"

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")


# --------------------------------------------------
# 1. Получение токена авторизации
# --------------------------------------------------

@pytest.fixture(scope="session")
def token():
    if not CLIENT_ID or not CLIENT_SECRET:
        pytest.skip("Не заданы SPOTIFY_CLIENT_ID и SPOTIFY_CLIENT_SECRET")

    credentials = f"{CLIENT_ID}:{CLIENT_SECRET}".encode()
    encoded_credentials = base64.b64encode(credentials).decode()

    response = requests.post(
        AUTH,
        headers={
            "Authorization": f"Basic {encoded_credentials}"
        },
        data={
            "grant_type": "client_credentials"
        },
        timeout=20
    )

    assert response.status_code == 200, (
        f"Ошибка авторизации: {response.status_code} {response.text}"
    )

    data = response.json()

    assert "access_token" in data

    return data["access_token"]


# --------------------------------------------------
# 2. Создание авторизованной сессии
# --------------------------------------------------

@pytest.fixture
def api(token):
    session = requests.Session()

    session.headers.update({
        "Authorization": f"Bearer {token}"
    })

    return session


# --------------------------------------------------
# 3. Получение ID существующего трека
# --------------------------------------------------

@pytest.fixture
def track_id(api):
    response = api.get(
        f"{API}/search",
        params={
            "q": "artist:Queen",
            "type": "track",
            "limit": 1
        },
        timeout=20
    )

    assert response.status_code == 200, response.text

    tracks = response.json()["tracks"]["items"]

    assert len(tracks) > 0, "Не удалось найти трек"

    return tracks[0]["id"]


# --------------------------------------------------
# 4. Позитивный тест поиска треков
# --------------------------------------------------

def test_search_track_positive(api):
    response = api.get(
        f"{API}/search",
        params={
            "q": "Twenty One Pilots",
            "type": "track",
            "limit": 5
        },
        timeout=20
    )

    assert response.status_code == 200, response.text

    data = response.json()

    assert "tracks" in data
    assert isinstance(data["tracks"]["items"], list)


# --------------------------------------------------
# 5. Негативный тест поиска с пустым запросом
# --------------------------------------------------

def test_search_empty_query_negative(api):
    response = api.get(
        f"{API}/search",
        params={
            "q": "",
            "type": "track"
        },
        timeout=20
    )

    assert response.status_code in (200, 400), response.text

    if response.status_code == 200:
        data = response.json()

        assert "tracks" in data
        assert isinstance(data["tracks"]["items"], list)


# --------------------------------------------------
# 6. Проверка поиска по запросу без ожидаемых совпадений
# --------------------------------------------------

def test_search_no_results(api):
    response = api.get(
        f"{API}/search",
        params={
            "q": "xyzqwerty123notarealtrack",
            "type": "track",
            "limit": 5
        },
        timeout=20
    )

    assert response.status_code == 200, response.text

    data = response.json()

    assert "tracks" in data

    tracks = data["tracks"]["items"]

    assert isinstance(tracks, list)
    assert len(tracks) <= 5


# --------------------------------------------------
# 7. Позитивный тест получения информации о треке
# --------------------------------------------------

def test_get_track_positive(api, track_id):
    response = api.get(
        f"{API}/tracks/{track_id}",
        timeout=20
    )

    assert response.status_code == 200, response.text

    data = response.json()

    assert "id" in data
    assert "name" in data
    assert "artists" in data
    assert "album" in data
    assert "duration_ms" in data

    assert isinstance(data["artists"], list)


# --------------------------------------------------
# 8. Негативный тест с неправильным ID трека
# --------------------------------------------------

def test_get_track_invalid_id(api):
    response = api.get(
        f"{API}/tracks/invalid_track_id_123",
        timeout=20
    )

    assert response.status_code in (400, 404), response.text


# --------------------------------------------------
# 9. Проверка запроса без токена
# --------------------------------------------------

def test_me_without_token():
    response = requests.get(
        f"{API}/me",
        timeout=20
    )

    assert response.status_code == 401, response.text


# --------------------------------------------------
# 10. Проверка запроса с неправильным токеном
# --------------------------------------------------

def test_me_with_invalid_token():
    response = requests.get(
        f"{API}/me",
        headers={
            "Authorization": "Bearer invalid-token"
        },
        timeout=20
    )

    assert response.status_code == 401, response.text


# --------------------------------------------------
# 11. Проверка неподдерживаемого HTTP-метода
# --------------------------------------------------

def test_delete_search_unsupported_method(api):
    response = api.delete(
        f"{API}/search",
        timeout=20
    )

    assert response.status_code in (400, 401, 403, 404, 405), response.text


# --------------------------------------------------
# 12. Проверка несуществующего адреса API
# --------------------------------------------------

def test_nonexistent_endpoint(api):
    response = api.get(
        f"{API}/nonexistent_endpoint_lab4",
        timeout=20
    )

    assert response.status_code in (404, 410), response.text


# --------------------------------------------------
# 13. Проверка структуры ответа о треке
# --------------------------------------------------

def test_track_response_contract(api, track_id):
    response = api.get(
        f"{API}/tracks/{track_id}",
        timeout=20
    )

    assert response.status_code == 200, response.text

    data = response.json()

    assert isinstance(data["id"], str)
    assert len(data["id"]) > 0

    assert isinstance(data["name"], str)
    assert isinstance(data["artists"], list)
    assert isinstance(data["album"], dict)

    assert isinstance(data["duration_ms"], int)
    assert data["duration_ms"] >= 0


# --------------------------------------------------
# 14. Граничный тест с нулевым значением limit
# --------------------------------------------------

def test_search_boundary_limit(api):
    response = api.get(
        f"{API}/search",
        params={
            "q": "test",
            "type": "track",
            "limit": 0
        },
        timeout=20
    )

    assert response.status_code in (200, 400), response.text
