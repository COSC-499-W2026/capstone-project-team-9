"""
Script for seeding development-only data that shouldn't end up in prod, like users.

Use:
```
docker compose exec backend python scripts/seed_dev.py
```

The `seed_dev()` function can also be used by other scripts
```
"""