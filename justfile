# This file provides simple aliases for common dev commands
# Run `just` with no arguments to list every recipe.

set dotenv-load := true

# Windows users run recipes in PowerShell (macOS/Linux use the default shell)
set windows-shell := ["powershell.exe", "-NoLogo", "-Command"]

# Postgres variables come from .env
db_user := env("POSTGRES_USER")
db_name := env("POSTGRES_DB")

# List all recipes
[private]
default:
    @just --list --unsorted

[private]
help: default

# ---------- App ----------

# Build/rebuild all containers and run the app
[group('App')]
build:
    docker compose up --build

# Run the app
[group('App')]
up:
    docker compose up

# Stop all containers
[group('App')]
down:
    docker compose down

# Stop all containers AND delete the data volume
[group('App')]
[confirm('⚠️  Are you sure you want to nuke all data volumes? (y/N)')]
nuke:
    docker compose down -v

# ---------- Tests ----------

backend_pytest := "docker compose exec -w /app/tests/backend backend pytest"

# Run backend tests; optionally pass a specific path (e.g `test_repos/`)
[group('Tests')]
test-backend path="":
    {{backend_pytest}} {{path}}

# --Run only backend unit tests
[group('Tests')]
test-backend-unit:
    {{backend_pytest}} -m unit

# --Run only backend integration tests
[group('Tests')]
test-backend-intg:
    {{backend_pytest}} -m integration

# Run frontend tests; optionally pass a specific path (e.g `api/`)
[group('Tests')]
test-frontend path="":
    docker compose exec frontend npm test tests/frontend/{{path}}

# Run backend AND frontend test suites
[group('Tests')]
test: test-backend test-frontend

# ---------- Database ----------

# Initialize the database
[group('Database')]
db-init:
    docker compose exec backend python scripts/init_db.py

# Seed reference data (languages, difficulties, etc.)
[group('Database')]
db-seed:
    docker compose exec backend python scripts/seed_reference.py

# Seed development-only data (e.g. fake users)
[group('Database')]
db-seed-dev:
    docker compose exec backend python scripts/seed_dev.py

# DEV ONLY: drop all tables, re-initialize, and re-seed
[group('Database')]
[confirm('⚠️  Are you sure you want to reset your development database? (y/N)')]
db-reset:
    docker compose exec backend python scripts/reset_db.py

# Open an interactive psql session (See README for psql tips)
[group('Database')]
psql:
    docker compose exec db psql -U {{db_user}} -d {{db_name}}

# ---------- Local venv (for your IDE only, not for running the app) ----------

# Create/recreate a venv and install dependencies
[unix, group('IDE')]
venv:
    [ -d .venv ] || python -m venv .venv
    .venv/bin/python -m pip install -e "./app/backend[test]"

# Create/recreate a venv and install dependencies
[windows, group('IDE')]
venv:
    if (-not (Test-Path .venv)) { python -m venv .venv }
    .venv\Scripts\python.exe -m pip install -e "./app/backend[test]"