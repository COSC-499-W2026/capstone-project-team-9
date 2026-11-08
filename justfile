# This file provides simple aliases for common dev commands
# Run `just` with no arguments to list every recipe.

set windows-shell := ["powershell.exe", "-NoLogo", "-Command"]

# List all recipes
default:
    @just --list

# ---------- App ----------

# Build (or rebuild) the containers and run the app
build:
    docker compose up --build