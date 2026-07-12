# Trackable

Trackable watches specific elements on static non-js rendered web pages (a price, a stock status, a
comment count, anything CSS can select) and records a snapshot every time
their content changes. It's a small clone of tools like changedetection.io,
built as a learning project around FastAPI, Celery, and Redis.

## How it works

- **FastAPI** exposes an HTTP API for registering/logging in, and for
  creating and listing "trackables" (a URL + a CSS selector + a check
  interval).
- **PostgreSQL** stores users, trackables, and a history of snapshots per
  trackable.
- **Celery beat** wakes up every 10 seconds and finds trackables whose
  `next_check_at` has passed.
- **Celery worker(s)** fetch each due trackable's page, run the CSS selector
  against it, and compare the extracted text against the last saved
  snapshot. If it changed (or this is the first check), a new snapshot row
  is saved.
- **Redis** is the message broker Celery uses to pass jobs from beat to the
  worker.

```
          ┌─────────┐        ┌───────────┐
  client ─┤ FastAPI │──────▶│ PostgreSQL │
          └─────────┘        └───────────┘
                                    ▲
          ┌─────────┐               │
          │  Redis  │◀──────┬───────┘
          └─────────┘       │
               ▲            │
          ┌────┴────┐  ┌────┴─────┐
          │  beat   │  │  worker  │──▶ fetches target URLs over HTTP
          └─────────┘  └──────────┘
```

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose

Python, Postgres, and Redis all run inside containers.

## Quickstart

```bash
git clone https://github.com/abde1khaliq/trackable_server.git
cd trackable_server
cp .env.example .env
docker compose up --build -d
```

Visit `http://localhost:8000` for a placeholder landing page (confirms the
API is up), or `http://localhost:8000/docs` for the interactive Swagger UI,
which is the easiest way to try requests without curl.

To stop everything:

```bash
docker compose down          # stop containers, keep the Postgres volume
docker compose down -v       # stop containers AND wipe the database
```

## Configuration

All configuration lives in `.env` (copy `.env.example` to get started).

| Variable        | Purpose                                                   |
|-----------------|------------------------------------------------------------|
| `DATABASE_URL`  | Async Postgres connection string (`+asyncpg`), used by the API and Alembic |
| `BACKEND_URL`   | This is just the backend url |
| `SECRET_KEY`    | Signs JWTs — set this to a real random string, especially outside local dev |
| `ALGORITHM`     | JWT signing algorithm (`HS256`)                             |
| `REDIS_BROKER`  | Redis connection string Celery uses as its broker          |

The Celery worker connects to Postgres with the same `DATABASE_URL`, but
swapped to the sync `psycopg` driver internally (see
`app/database/sync_session.py`).

## Using the API

The API is JWT-protected: register, log in to get a token, then include it
as a Bearer token on trackable requests.

**1. Register a user**

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
        "first_name": "Ada",
        "last_name": "Lovelace",
        "email": "ada@example.com",
        "password": "a-real-password"
      }'
```

**2. Log in**

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "ada@example.com", "password": "a-real-password"}'
```

This returns an `access_token`:

```bash
export TOKEN="paste-the-access-token-here"
```

**3. Create a trackable**

`tracked_element_selector` takes a real CSS selector (not just a bare class
name). This matters as soon as more than one element on the page shares a
class. See the built-in test page below for examples of disambiguating with
`[data-*]` attributes or `:nth-of-type`.

```bash
curl -X POST http://localhost:8000/trackables/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
        "name": "Test timestamp",
        "url": "http://test-page:8080",
        "interval_minutes": 1,
        "tracked_element_selector": ".tracked-timestamp"
      }'
```

Note the hostname: containers reach each other by service name on the
Docker network, so from inside the `worker`/`api` containers the test page
is `http://test-page:8080`, not `http://localhost:8080` (that's only for
your host browser).

**4. List your trackables and their latest snapshot**

```bash
curl http://localhost:8000/trackables/ \
  -H "Authorization: Bearer $TOKEN"
```

## Trying it out with the built-in test page

The `test-page` service (`tests/test_server.py`) serves a page with a mix of
elements useful for exercising the watcher without depending on a real
website:

| Selector                             | Behavior                                   |
|---------------------------------------|---------------------------------------------|
| `.tracked-timestamp`                  | Changes on every single request             |
| `.tracked-price`                      | Changes roughly every 10 seconds            |
| `.tracked-stock`                      | Flips roughly every 30 seconds              |
| `.tracked-static`                     | Never changes — good negative test          |
| `[data-product="1"] .price_color`     | Disambiguates a class shared by two elements|
| `[data-product="2"] .price_color`     | The other one                                |
| `.price_color:nth-of-type(2)`         | Same disambiguation, via position instead   |

Create a few trackables against different selectors and watch
`docker compose logs -f worker`, you'll see new snapshots appear for the
ones that change and nothing for `.tracked-static`, which is the signal that
the diffing logic itself is working correctly rather than falsely flagging
every check as a change.

## Database migrations

Migrations run automatically on container startup (`alembic upgrade head`,
in `entrypoint.sh`) so you don't need to run them by hand for normal use.

If you add a new model field and need to generate a new migration:

```bash
docker compose exec api alembic revision --autogenerate -m "describe your change"
docker compose restart api worker beat
```

## Troubleshooting

- **`api` keeps restarting** — check `docker compose logs api`; usually
  either `.env` wasn't created (`cp .env.example .env`) or `DATABASE_URL`
  doesn't match the `POSTGRES_*` credentials.
- **Worker never picks up a due trackable** — check `docker compose logs
  beat` first; beat has to be running and able to reach Redis for the
  worker to ever receive a job.
- **A trackable never gets a new snapshot** — check `docker compose logs
  worker` for a "Check failed" warning; this usually means the CSS selector
  didn't match anything on the current page, or the target site couldn't be
  reached.