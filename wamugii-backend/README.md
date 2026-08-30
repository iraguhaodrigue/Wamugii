# WAMUGII TECH SOLUTIONS — Backend (Sprint 1)

The foundation of the WAMUGII platform: **FastAPI + PostgreSQL + SQLAlchemy 2 +
Alembic**, with working **authentication, users, and roles** (ADMIN / STAFF /
CLIENT). Everything else in your plan (projects, hosting, store, payments, SaaS)
gets built on top of this — one module at a time.

## What is inside

```
app/
  core/       config, database connection, security (password + JWT)
  models/     database tables (User for now)
  schemas/    request/response shapes (Pydantic)
  crud/       database operations
  api/v1/     the endpoints (auth, users) + router
  main.py     the app
  seed.py     creates your first admin user
alembic/      database migrations
Dockerfile, docker-compose.yml, requirements.txt, .env.example
```

## Fastest way to run (Docker) — recommended

You already use Docker, so this is the quickest.

```bash
cp .env.example .env          # then open .env and set a real SECRET_KEY
docker compose up --build
```

That single command will:
1. start PostgreSQL,
2. run database migrations,
3. create the admin user,
4. start the API on http://localhost:8000

Open the interactive docs: **http://localhost:8000/docs**

> First time only: the app needs one migration file. If `alembic upgrade head`
> finds nothing to run, create it once (see "Create the first migration" below),
> then `docker compose up` again.

## Run without Docker (local)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Edit .env: change the DATABASE_URL host from "db" to "localhost"
# (you need a PostgreSQL running locally with the wamugii user/db)

alembic revision --autogenerate -m "create users table"
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload
```

## Create the first migration

Alembic reads your models and writes the SQL for you.

```bash
alembic revision --autogenerate -m "create users table"
alembic upgrade head
```

Every time you add or change a model later, run those two lines again with a new
message. This is how your database grows safely.

## Test it in the browser (no code needed)

1. Go to http://localhost:8000/docs
2. `POST /api/v1/auth/register` — create a user.
3. Click the green **Authorize** button, put the user's **email** in the
   *username* box and the password, click Authorize.
4. Now `GET /api/v1/auth/me` returns your user. Protected routes work.

## The endpoints

| Method | Path                     | Who can use it        |
|--------|--------------------------|-----------------------|
| GET    | /health                  | anyone                |
| POST   | /api/v1/auth/register    | anyone (creates CLIENT)|
| POST   | /api/v1/auth/login       | anyone                |
| POST   | /api/v1/auth/refresh     | anyone with a refresh token |
| GET    | /api/v1/auth/me          | logged-in user        |
| POST   | /api/v1/auth/logout      | logged-in user        |
| GET    | /api/v1/users/me         | logged-in user        |
| GET    | /api/v1/users            | ADMIN, STAFF only     |
| GET    | /api/v1/users/{id}       | ADMIN, STAFF only     |

## Roles

- **ADMIN** — you. Full control (created by `app/seed.py`).
- **STAFF** — your team members.
- **CLIENT** — your customers (created automatically on register).

To protect any future endpoint, add one line:
`dependencies=[Depends(require_roles(Role.ADMIN))]`

## Security notes (already done for you)

- Passwords are hashed with **Argon2** — never stored as plain text.
- Access token (short life) + refresh token (long life), both signed with your
  `SECRET_KEY`. **Change SECRET_KEY in .env before deploying.**
- Role checks stop a CLIENT from reaching admin data.

## Next: Sprint 2

On top of this foundation, add (each is a model + schema + crud + one router
file, exactly like `user`): **Services → Quote Requests → Projects →
Milestones**. Same pattern every time, so it gets faster.
