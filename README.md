# Zlagoda

AIS for a grocery mini-supermarket (KMA databases course project). FastAPI + raw SQL (psycopg 3, no ORM), Jinja2 server-side templates, PostgreSQL 16 in Docker.

## Prerequisites

- Install uv ```powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"``` (via powershell)
- Docker with the compose plugin

## Setup

```sh
git clone git@github.com:imaro56/Zlagoda.git && cd Zlagoda

# 1. Python deps
uv sync

# 2. Environment
cp .env.sample .env

# 3. Database port 5433 PGSQL
docker compose up -d

# 4. Seed the admin account (login: admin, password: password)
uv run python -m app.scripts.seed

# 5. Run the app
uv run uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/login and sign in with `admin` / `password`.
