# Homework: LocalGPT chat

FastAPI homework project implementing a ChatGPT-like application with registration, JWT access tokens, Redis refresh sessions, GitHub OAuth, PostgreSQL migrations and a server-rendered UI.

## Architecture

The project uses **server-rendered HTML**, so it follows **MVC**:

- **Models**: `app/models/*` - SQLAlchemy database models.
- **Views**: `app/templates/*` and `app/static/*` - HTML/CSS/JS interface.
- **Controllers**: `app/controllers/*` - FastAPI route handlers.
- **Services**: `app/services/*` - business logic for auth, chats, Redis sessions, OAuth and LLM calls.

## Run

```bash
cd homework
cp .env.example .env
# optional: put a GGUF model into homework/model.gguf
# optional: fill GitHub OAuth env variables in .env
docker compose up --build
```

Open: `http://localhost:8000`

Docs: `http://localhost:8000/docs`

## API

Auth:

- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/refresh`
- `POST /auth/logout`
- `GET /auth/github/login`
- `GET /auth/github/callback`

Protected chat API, requires `Authorization: Bearer <access_token>` or auth cookie:

- `GET /api/chats`
- `POST /api/chats`
- `GET /api/chats/{chat_id}`
- `POST /api/chats/{chat_id}/messages`
- `DELETE /api/chats/{chat_id}`

## Database

PostgreSQL schema is managed by Alembic migration `alembic/versions/0001_initial.py`.

Tables: `users`, `chats`, `messages`.

Redis refresh session keys: `refresh:{token}` with TTL = 30 days.

## LLM

`app/services/llm_service.py` uses `llama-cpp-python` when `model.gguf` exists. Without a model the app stays runnable and returns a demo answer explaining how to enable local inference.
