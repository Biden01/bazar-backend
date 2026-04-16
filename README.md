# Bazar Digital — Backend

REST API для маркетплейса [Bazar Digital Taraz](https://bazar-digital.kz). Построен на FastAPI с асинхронным PostgreSQL и Redis.

## Стек

- **FastAPI** 0.109 + **Uvicorn**
- **SQLAlchemy 2.0** (async) + **asyncpg** + **PostgreSQL**
- **Redis** — кэш, OTP, rate limiting
- **Alembic** — миграции
- **OpenAI API** — AI-ассистент
- **Docker / Docker Compose**

## API-модули

| Префикс | Описание |
|---------|----------|
| `/v1/auth` | Регистрация, вход (OTP + пароль), JWT токены |
| `/v1/users` | Профиль, настройки, подписки |
| `/v1/products` | Каталог товаров, поиск, категории |
| `/v1/orders` | Заказы, статусы, история |
| `/v1/inventory` | Управление складом продавца |
| `/v1/debts` | Долговые обязательства |
| `/v1/chats` | Чат покупатель–продавец |
| `/v1/notifications` | Push-уведомления |
| `/v1/b2b` | B2B прайс-группы, верификация |
| `/v1/documents` | Документы (накладные, счета) |
| `/v1/upload` | Загрузка файлов/изображений |
| `/v1/calculator` | Калькулятор цен |
| `/v1/ai` | AI-ассистент (OpenAI) |

Документация Swagger: `http://localhost:8000/docs` (только в `DEV_MODE=true`)

## Быстрый старт (Docker)

```bash
# Скопировать и заполнить переменные окружения
cp .env.example .env

# Запустить
docker compose up -d
```

## Быстрый старт (локально)

```bash
# Создать виртуальное окружение
python -m venv .venv
source .venv/bin/activate

# Установить зависимости
pip install -r requirements.txt

# Применить миграции
alembic upgrade head

# Запустить
uvicorn app.main:app --reload
```

## Переменные окружения

| Переменная | Описание |
|------------|----------|
| `DATABASE_URL` | PostgreSQL DSN (`postgresql+asyncpg://...`) |
| `REDIS_URL` | Redis DSN |
| `JWT_SECRET` | Секрет для подписи JWT (min 64 символа) |
| `JWT_ALGORITHM` | Алгоритм JWT (по умолчанию `HS256`) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Время жизни access token |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Время жизни refresh token |
| `CORS_ORIGINS` | Разрешённые origins (через запятую) |
| `DEV_MODE` | `true` — OTP не проверяется, Swagger включён |
| `OPENAI_API_KEY` | Ключ OpenAI для AI-ассистента |
| `ADMIN_SECRET` | Секрет для admin-эндпоинтов |

## Тесты

```bash
pytest
```

## Структура проекта

```
app/
  main.py         # Точка входа, middleware, роутеры
  config.py       # Настройки (pydantic-settings)
  database.py     # Сессия БД
  dependencies.py # FastAPI зависимости (auth, pagination...)
  models/         # SQLAlchemy модели
  schemas/        # Pydantic схемы
  routers/        # Эндпоинты по модулям
  services/       # JWT, OTP, пароли
  utils/          # Пагинация, Redis-хелперы
alembic/
  versions/       # Миграции
tests/            # pytest
```
