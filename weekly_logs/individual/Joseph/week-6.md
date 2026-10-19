## For PR #113:

As part of requirement "Location check" (the system shall verify that the user's location is on campus before starting the game loop), the player needs to open the app, tap Play, have their device location sent to the backend, and either be allowed to start or see a blocked message.

Therefore, I implemented code so that players can use the Play button in a minimal Vue 3 + Vite frontend, which gets the browser's GPS position, sends it to the existing `POST /location/verify` endpoint, and shows the allowed/blocked result. This is the first connection between the frontend and the backend. It also adds a `frontend` service to `docker-compose.yml` so the frontend runs with the same `docker compose up` as the backend.

Data modeling receipts are not applicable because this PR does not change the database or validate user data. The backend schema already validates the coordinates.

When I reviewed the code i did not find any issues

The PR does not contain any temporary workaround because the frontend structure is intended as the long-term base. Requests go through the Vite `/api` proxy instead of a hardcoded backend address.

The PR only contains small functions that are 1 to [12] lines long. The longest is `play()` in `PlayView.vue` at about [12] lines, and the others are `getCurrentCoords` [8], `request` [8], `get` and `post` [1], and `verifyLocation` [1].

I did [read through each file and searched for repeated values and unused imports] to ensure my feature contribution does not contain any of the following:
- hardcoded values (the API base path is a named constant in `client.js`)
- duplicate code
- dead code
- unnecessary function calls
- excessive conditional logic
- deep nesting
- high cyclomatic complexity
- classes/modules/functions with many unrelated responsibilities


This work is written in `src/frontend/` because functional code must be in `src/`, and the frontend is a self-contained package with its own `package.json` and config. Inside it, `api/` holds the only `fetch` calls (one file per backend router, so `location_router.py` maps to `location.js`), `views/` holds screens, and `utils/` holds plain helpers. This mirrors the layered backend, so one feature touches the same-named file in each layer. `package-lock.json` is auto-generated and committed so everyone installs identical dependency versions.

This work belongs in process "Verify location" in the Game loop DFD because it is the front end that sends the player's coordinates and displays the allowed/blocked decision. In the system architecture diagram it is the Vue front-end box calling the FastAPI routers over HTTP.

Testing receipts PR#125:

The functionality works correctly because the happy path tests `get() prefixes /api and returns parsed JSON`, `post() sends a JSON body with the POST method`, `verifyLocation posts the coordinates to /location/verify`, `PlayView shows the allowed message on campus` and `PlayView sends the device coordinates to the API` passed.

I wrote tests to cover abnormal situations involving the backend returning a non-ok status (`throws when the response is not ok`), the user denying location access (`shows an error when location access fails`, which also asserts the API is never called) and the backend call failing (`shows an error when the backend call fails`), and they passed.

I checked that the negative case involving an off-campus result (`shows the blocked message off campus`) displayed the 🚫 and the server's message as expected, and that `disables the button while waiting` prevents repeated clicks during a request.

I also tested manually in Brave by spoofing the location with DevTools. On-campus coordinates (49.9394, -119.3948) returned allowed and off-campus coordinates (49.2827, -123.1207) returned blocked, which confirms the full chain of browser GPS, Vite proxy, FastAPI and response, which the mocked tests cannot cover.

Among these tests, the `client` and `location` API tests are unit tests. The `PlayView` tests are component tests that mount the view with its API and geolocation modules mocked. Full integration tests are not required because the real integration between the frontend and backend was verified manually, and the backend endpoint is already covered by its own integration tests in `tests/test_location_router.py`.

These tests are included in the directory `src/frontend/tests/`.

This new PR did not break anything else in the system because I ran `docker compose exec backend pytest` and `docker compose exec frontend npm test`, and all tests passed.


## For PR #125:

As part of the team contract's testing practices (test-driven development, unit testing and CI), the developer needs to run the frontend tests with one command locally and have GitHub run them automatically when a PR is opened.

Therefore, I implemented code so that all developers on the team can run frontend tests with Vitest, using `@vue/test-utils` for components and jsdom to simulate a browser. It adds `test` and `test:watch` scripts to `package.json`, a `test` block in `vite.config.js` so Vitest reuses the existing Vite config, and a "Run Frontend Tests in Docker" step in `.github/workflows/tests.yml`. I also added frontend test instructions to the README next to the pytest ones.

Data modeling receipts are not applicable because this PR does not change the database or validate user data.

When I reviewed `package.json` and `vite.config.js`, I noticed the new dependencies were not available in the running frontend container, because it only runs `npm install` on startup. Therefore, I restarted it with `docker compose up` so the packages installed, and confirmed `npm test` ran.

When I reviewed the CI step, I used `npm ci` instead of `npm install` so CI installs exactly what `package-lock.json` specifies and fails if it is out of sync with `package.json`. [Add a problem if you hit a real one, e.g. a CI failure.]

The PR does not contain any temporary workaround because the test configuration is the long-term setup. It contains configuration and no application logic.

The PR contains no functions. It has configuration only, with a [5]-line `test` block and a [3]-line CI step.

I did [read through each changed file and checked for repeated values] to ensure my contribution does not contain hardcoded values, duplicate code, dead code, unnecessary calls, excessive conditional logic, deep nesting, high cyclomatic complexity, or modules with many unrelated responsibilities.

This work is written in `src/frontend/package.json` and `src/frontend/vite.config.js` because Vitest reads its configuration from the frontend project root, which is also where `node_modules` lives. The CI step is in `.github/workflows/tests.yml` because GitHub only runs workflows located in `.github/workflows`.

This work belongs in no DFD process because it adds test infrastructure and does not contain application logic.

Testing receipts PR#125 [number]:

This PR is the testing setup. Its functionality works correctly because running `docker compose exec frontend npm test` discovers and passes the [number] frontend tests (written for the frontend setup, see that log's testing section), and the new CI step passed on the PR. 

Among these tests, no new tests were written in this PR because it is configuration only, so the sections for unit and integration tests are not applicable.

This new PR did not break anything else in the system because I ran `docker compose exec backend pytest` and all backend tests still pass. 