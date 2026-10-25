"""
Script for initializing the database.
Use:
```
docker compose exec backend python scripts/init_db.py
```
"""

import core.db as db

if __name__ == "__main__":
    db.init_db()
    print("Tables created.")