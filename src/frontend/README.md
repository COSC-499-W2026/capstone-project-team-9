# Frontend conventions

Vue 3 + Vite + vue-router. Runs via `docker compose up` at http://localhost:5173.

## Where things go
| Folder | Contains | Rules |
|---|---|---|
| `views/` | One file per screen, named `XxxView.vue` | Handles screen state and calls `api/`. Registered in `router/index.js`. |
| `components/` | Reusable UI pieces | Receive data via props, emit events. No `api/` calls unless self-contained (like BackendStatus). |
| `api/` | One file per backend router (`location_router.py` -> `location.js`) | Only place URLs and `fetch` live. Views never call `fetch` directly. |
| `utils/` | Plain JS helpers | No Vue imports. |

## Adding a feature
1. Add the backend endpoint (router, service, schema).
2. Add a function in `api/<feature>.js`.
3. Create `views/<Feature>View.vue` and call the api function.
4. Add the route in `router/index.js` and a link in `App.vue`.
5. Pull anything repeated or over ~150 lines into `components/`.

## Rules
- `App.vue` stays a shell; no feature logic.
- Backend calls always go through `/api/...` (the Vite proxy), never a hardcoded host.
- Use `<script setup>` in every component.