This week, we focused on setting up the project foundation, with the goal of giving everyone a working, shared codebase to build features on.

The work was distributed so that Joseph focused on the FastAPI backend setup and the Docker setup, as well as the level 1 DFDs for the game loop and student view. Eric focused on setting up Pytest, and Nash and Ian focused on the remaining DFD diagrams as well as system architecture and design. We considered having everyone start on their own features right away, but we did not go with it because there was no shared codebase yet, and it would have led to merge conflicts and inconsistent setups.

Based on the merged PRs, the backend starting with `docker compose up --build`, `/health` returning `{"status":"ok"}`, and Pytest running, we met this goal because a teammate can clone the repo, follow the README, and run the system and its tests.

By reading through the Dockerfile and docker-compose.yml, Joseph found that the Uvicorn start command was written in both files, which is similar logic implemented twice. Therefore, the duplicate code was removed from the compose file. Now, the team can confirm that the code base does not contain similar logic implemented multiple times, many dependencies between modules, or changes in one component that require changes elsewhere.

With everyone's newly merged work for this week, the system DFD has been created for the first time.

The specific changes include adding level 1 diagrams for the game loop, student view, student management, login, game item management, and class management . We considered checking the player's GPS when the app opens, but we did not go with it because students should be able to browse from anywhere, and the check only matters when a game starts.

With everyone's newly merged work for this week, the system architecture diagram has been created for the first time. The specific changes include adding the diagram showing [the Vue front end, the FastAPI backend, PostgreSQL, and how they connect]. We considered alternative architectural components such as organizing the backend by feature instead of by layer, but we did not go with it because the layered structure keeps routing, logic, and data access separate and is easier for future teams to follow. We considered alternative dependencies such as Flask and unittest, but we did not go with them because FastAPI gives us built-in validation and auto-generated docs, and Pytest has simpler syntax.

Author of this weeks team log: Joseph Mondelli