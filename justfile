# This file provides simple aliases for common dev commands
# Run `just` with no arguments to list every recipe.

set dotenv-load := true

# Windows users run recipes in PowerShell (macOS/Linux use the default shell)
set windows-shell := ["powershell.exe", "-NoLogo", "-Command"]

# Postgres username comes from .env (POSTGRES_USER is a guess; adjust to match yours)
db_user := env("POSTGRES_USER", "postgres")
db_name := "language_game_db"

# List all recipes
default:
    @just --list

# ---------- App ----------

# Build (or rebuild) the containers and run the app
build:
    docker compose up --build

# Run the app
up:
    docker compose up

# Stop all containers
down:
    docker compose down

# Stop all containers AND delete the data volume
nuke:
    docker compose down -v

# ---------- Tests ----------

# Run backend tests; optionally pass a path relative to tests/, e.g. `just test-backend test_users.py`
test-backend *args:
    docker compose exec backend pytest {{args}}

# Run frontend tests
test-frontend *args:
    docker compose exec frontend npm test {{args}}

# Run the backend and frontend test suites
test: test-backend test-frontend

# ---------- Database ----------

# Initialize the database
db-init:
    docker compose exec backend python scripts/init_db.py

# Seed reference data (languages, difficulties, etc.)
db-seed:
    docker compose exec backend python scripts/seed_reference.py

# Seed development-only data (e.g. fake users)
db-seed-dev:
    docker compose exec backend python scripts/seed_dev.py

# DEV ONLY: drop all tables, re-initialize, and re-seed
db-reset:
    docker compose exec backend python scripts/reset_db.py

# Open an interactive psql session (see README for psql tips)
psql:
    docker compose exec db psql -U {{db_user}} -d {{db_name}}

# ---------- Local venv (for your IDE only, not for running the app) ----------

# Create a venv and install dependencies (then activate it yourself; see README)
[unix]
venv:
    python -m venv .venv
    .venv/bin/python -m pip install -e "./app/backend[test]"

[windows]
venv:
    python -m venv .venv
    .venv\Scripts\python.exe -m pip install -e "./app/backend[test]"