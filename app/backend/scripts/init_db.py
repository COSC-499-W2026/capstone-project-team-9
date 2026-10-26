"""
Script for initializing the database.

Use:
```
docker compose exec backend python scripts/init_db.py
```
"""
from core.db import init_db

if __name__ == "__main__":
    init_db()
    print("Tables created.")