**For PR #25:**

As part of the project setup for the maintainability goal in our proposal's Value Proposition (and as the foundation for every functional requirement in the work breakdown), the developer needs to clone the repo, create a virtual environment, install dependencies, start the server, and confirm the API responds at `/health` and `/docs`.

Therefore, I implemented code so that all developers on the team can run a FastAPI backend locally. It includes a health check endpoint, CORS configuration for the Vue dev server, the layered folder structure (routers, services, repositories, schemas, models), a README with setup steps, and a `.gitignore`.

Data modeling receipts are not applicable because this PR does not change the database or validate user data.

When I reviewed `src/main.py` and `src/routers/health.py` for this functionality, I did not find any problems because I ran `fastapi dev src/main.py`, confirmed `/health` returns `{"status":"ok"}`, confirmed `/docs` loads, and read through each line to confirm I understood what it does.

The PR does not contain any temporary workaround because it only contains the standard FastAPI app setup, with no placeholder logic.

The PR only contains small functions. `health_check` is 2 lines long, and `main.py` has no functions, only app configuration.

I did read through the files and search for unused imports and duplicated code to ensure my contribution does not contain hardcoded values, duplicate code, dead code, unnecessary function calls, excessive conditional logic, deep nesting, high cyclomatic complexity, or modules with many unrelated responsibilities.

The review by Ian identified missing instructions. Therefore, I added instructions on running the system to the README.

This work is written in the new files `src/main.py` and `src/routers/health.py` because the app entry point is separate from feature routers so `main.py` stays small as features are added.

---

**For PR #29:**

As part of the maintainability goal in our proposal's Value Proposition (and the plan to let other universities host their own instances), a developer needs to install Docker Desktop, clone the repo, run `docker compose up --build`, open `/health` and `/docs` in the browser, and edit a file in `src/` to see the server reload.

Therefore, I implemented code so that all developers on the team, and future maintainers, can run the FastAPI backend in an identical container without installing Python or the dependencies themselves. It adds a `Dockerfile`, a `docker-compose.yml`, a `.dockerignore`, and a Docker section in the README.

Data modeling receipts are not applicable because this PR does not change the database or validate user data.

When I reviewed the `Dockerfile` and `docker-compose.yml` for this functionality, I did not find any problems because I ran `docker compose up --build`, confirmed Uvicorn started, confirmed `/health` returned `{"status":"ok"}` and `/docs` loaded, and edited a file in `src/` to confirm the server reloaded.

The PR does not contain any temporary workaround because it contains configuration and no application logic.

The PR contains no functions. It has configuration files only, with the `Dockerfile` at 13 lines and the compose file at about 7 lines.

By reading both files and checking for repeated values, I found that my contribution contained duplicate code: the Uvicorn start command appears in both the `Dockerfile` and the compose file, and the port and `/app` path appear in several places. Therefore, I removed the duplicate command from the compose file.

Now, I can confirm that my contribution does not contain duplicate code, dead code, unnecessary calls, excessive conditional logic, deep nesting, high cyclomatic complexity, or modules with many unrelated responsibilities.

This work is written in the new files `Dockerfile` and `docker-compose.yml` at the repo root because Docker looks for them there and uses the repo root as the build context. The application code stays in `src/` as our required structure specifies, and `.dockerignore` keeps the venv, `.git`, and secrets out of the image.

This work does not belong to a DFD process because it is infrastructure and does not transform data. It maps to the deployment view of our system architecture diagram instead.