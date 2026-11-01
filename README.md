# ЛР4 — Spotify Web API: API-тестирование и CI/CD

## Состав проекта
- `tests/test_spotify_api.py` — 11 API-сценариев на pytest + requests.
- `.github/workflows/api-tests.yml` — запуск тестов на push/PR в `main` и `master`.
- `requirements.txt` — зависимости.
- `postman/spotify_collection.json` — коллекция ручных запросов.

## Запуск локально
1. Установить Python 3.10+.
2. `python -m venv .venv`
3. Windows: `.venv\\Scripts\\activate`; Linux/macOS: `source .venv/bin/activate`
4. `pip install -r requirements.txt`
5. Задать переменные окружения `SPOTIFY_CLIENT_ID` и `SPOTIFY_CLIENT_SECRET`.
6. `pytest`

Без ключей Spotify тесты, которым нужен OAuth, будут пропущены; тесты без токена выполняются отдельно. Секреты нельзя записывать в исходный код или коммитить в репозиторий.

## Настройка GitHub Actions
В репозитории открыть Settings → Secrets and variables → Actions и добавить repository secrets:
- `SPOTIFY_CLIENT_ID`
- `SPOTIFY_CLIENT_SECRET`

При необходимости добавить variable `SPOTIFY_TRACK_ID` с ID доступного трека. Затем отправить проект в GitHub и проверить вкладку Actions. Отчёты сохраняются как артефакт `spotify-api-test-reports`.

## Важное замечание
Spotify может менять доступность endpoints и правила доступа в зависимости от типа приложения, режима разработки и выданных scopes. Поэтому проверяются документированные коды либо допустимые варианты для неоднозначных отрицательных сценариев. Фактический успешный прогон CI нельзя утверждать до запуска в репозитории с действующими секретами.
