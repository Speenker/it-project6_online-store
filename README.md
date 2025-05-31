# Минимальная архитектура онлайн-магазина

## Архитектура
- **Streamlit UI (FE)** — фронтенд
- **FastAPI API** — бэкенд
- **PostgreSQL** — основная БД
- **Elasticsearch** — поиск
- **Kafka** — события
- **ClickHouse** — аналитика

## Запуск

```bash
docker-compose up --build
```

## Перекомпиляция и перезапуск после изменений
Если вы внесли изменения в код или зависимости, рекомендуется полностью пересобрать и перезапустить проект:

```bash
docker-compose down
# (опционально) удалить тома, если нужно сбросить данные: docker-compose down -v
# пересобрать и запустить заново
docker-compose up --build
```

## Проверка
- Перейти на [http://localhost:8501](http://localhost:8501) — Streamlit UI
- Нажать кнопку "Проверить backend" для теста связи с FastAPI

## Структура
- `backend/` — FastAPI приложение
- `frontend/` — Streamlit приложение 