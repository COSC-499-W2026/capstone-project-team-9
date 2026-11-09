# For PR #249:

As part of requirement #170 (basic frontend for the play screen), the student needs to open the Play screen, choose a language, difficulty and number of questions, pass the campus location check, press Play, and then see the first clue with their progress through the game.

Therefore, I implemented code so that students can:

- pick a language and difficulty loaded from the backend
- pick a question count limited to what is actually available for that language and difficulty ("None available" when there are none)
- start a game after the location check passes. This creates a game, starts a play and opens `/play/:playId`.
- see a full-screen clue view with an exit button, a "Clue N of M" progress bar, a Listen card with a placeholder audio player, and a disabled Skip button
- see clear states for loading, a game that doesn't exist, a game that failed to load, and a finished game
- see the backend's actual error message when something fails, instead of a generic error

This PR does not change the database or validate user data. The backend owns question availability and game creation, and the frontend only displays what it returns. No Data Modeling receipts are required.

When I reviewed the generated `ClueAudio.vue` audio player component, I noticed it had grown past what issue #170 asks for. It also depended on clue audio that doesn't exist on the backend yet, so it couldn't be tested properly in this PR. Therefore, I moved the real audio player into its own upcoming PR and replaced it with `ClueAudioPlaceholder.vue`, a disabled player labelled "Clue audio coming soon". That kept this PR focused on game setup and the clue screen.

When I reviewed the generated `client.js` error handling, I noticed failed requests only returned a generic error. The Play screen couldn't tell the student why a game didn't start, for example when no questions exist for a language yet. Therefore, I made `request()` attach the HTTP status and, when the response is JSON with a string `detail`, the backend's message. The Play screen now shows that message directly.

The PR does not contain any temporary workaround. The unfinished parts (clue audio and Skip) are shown as clearly disabled controls with TODO comments that point to the PRs that will replace them. No fake logic stands in for missing backend behaviour. Skip stays disabled until the backend has a skip endpoint, rather than being faked on the frontend.

The PR only contains small functions that are 1–22 lines long. The API wrappers in `game.js` are 1–5 lines each, `load()` in `ClueView.vue` is about 9 lines, and the longest is `play()` in `PlayView.vue` at about 22 lines.

I did the following to ensure that my feature contribution does not contain any of the following:

- **Hardcoded values:** languages, difficulties and the allowed question range all come from the backend (`getLanguages`, `getDifficulties`, `getGameLengths`). The default question count is the named constant `DEFAULT_NUM_CLUES = 3`, clamped to the backend's `{min, max}` range. The bar count is the named constant `BAR_COUNT = 36`. Colours, radii and spacing are CSS variables in `game.css`.
- **Duplicate code:** shared button, spinner and colour styles live once in `game.css`, scoped under `.game`, instead of being repeated in each view. The create-game then start-play sequence is wrapped once in `startGame()`. Error-detail extraction happens once in `client.js` instead of in every view.
- **Dead code:** the original audio player component was removed from this PR entirely rather than left unused.
- **Unnecessary function calls:** game lengths are only re-fetched when language or difficulty changes, through a single `watch`.
- **Excessive conditional logic, deep nesting and high cyclomatic complexity:** views branch only on simple states (loading, error, complete), and the clue number is a single `Math.min(solved_clues + 1, total_clues)`.
- **Mixed responsibilities:** API calls live in `api/game.js`, display lives in the views, and the audio placeholder is its own component.

Now, I can confirm that my feature contribution does not contain any of the following:

- hardcoded values
- duplicate code
- dead code
- unnecessary function calls
- excessive conditional logic
- deep nesting
- high cyclomatic complexity
- classes/modules/functions with many unrelated responsibilities

The reviews by Jmondelli and MaddoxJTG identified no problems. Both approved after running the frontend and backend test suites locally, so no changes were needed.

This work is written in the new files `api/game.js`, `views/ClueView.vue`, `components/ClueAudioPlaceholder.vue` and `styles/game.css`, and in the existing files `views/PlayView.vue`, `api/client.js` and `router/index.js`. The existing frontend separates backend calls (`api/`), routed screens (`views/`) and reusable pieces (`components/`). Game endpoints get their own API module next to the shared client, and the clue screen is a new route because it is a separate step after setup.

This work belongs in process 1, Game loop, in the level 0 DFD, and in the Game loop level 1 DFD (`docs/system-design/data-flow-diagrams/DFD-1-game-loop.md`), because it is the player-facing side of a single game session from the Play click onward:

- **1 Verify location:** pressing Play sends the player's GPS position, and out-of-boundary players are blocked before a game starts.
- **2 Set up game:** the player's language, difficulty and length settings are sent to the backend, which selects the targets from the game items.
- **3 Play audio clue:** the Listen card is the entry point for the clue audio, shown as a placeholder until the audio PR.
- **5 Score and track:** the clue screen reads the play state to show progress ("Clue N of M") and completion, with Skip reserved here for when the backend supports it.

---

# For PR #249 (tests):

The functionality works correctly because the happy path tests involving the following passed:

- `starts a game and opens the first clue when on campus`
- `lists the languages and the available question counts`
- `lists the difficulties`
- `starts the game with the picked language and question count`
- `starts the game with the picked difficulty`
- `loads the play and shows progress for the first clue`
- `numbers the clue by how many are solved`
- `shows the audio placeholder`
- `shows the finish screen when the play is complete`
- `goes back to the start screen from the exit button`
- the five `game api` tests: `getGameLengths() passes the combo as query params`, `createGame() posts the settings in the backend field names`, `startPlay() posts to the game plays route`, `getPlayState() gets the play`, and `startGame() creates a game, starts a play and returns its id`

I wrote tests to cover abnormal situations involving the following and they passed:

- `defaults to fewer questions when fewer are available`
- `shows the reason when the game cannot be started`
- `shows an error when the options fail to load`
- `shows a message when the play does not exist`
- `shows a message when the play fails to load`
- `attaches the status and backend detail to the error`

I checked that these negative cases involving the following failed as expected:

- `does not start a game off campus`
- `does not start a game when the language has no questions`
- `shows a Skip button that is disabled until the backend supports skipping`

When I reviewed the existing `PlayView.test.js` tests, I noticed they no longer matched the component, because `PlayView` now loads languages and difficulties when it mounts. Without a mock, those calls would hit the real API and the tests would fail or depend on a running backend. Therefore, I mocked the new `api/game.js` module in that test file so the original location tests still run in isolation.

Among these tests, all of them are unit tests, and integration tests are not required because the views only talk to the backend through `api/game.js`, which is unit-tested against the exact routes and field names the backend expects. The backend endpoints themselves are covered by the backend's own test suite.

These tests are included in these directories:

- `tests/frontend/api/` (`client.test.js`, `game.test.js`)
- `tests/frontend/views/` (`ClueView.test.js`, `PlayView.test.js`)

This new test PR did not break anything else in the system because the full frontend suite (47 tests) passes with `just test-frontend`, and both reviewers (Jmondelli and MaddoxJTG) ran the frontend and backend suites on their own machines and confirmed they all pass.





For PR #251:

As part of requirement Upload image, the user needs to open a clue, tap Take a photo, point the back camera at the room sign, take the photo (or retake it), and press Submit answer, then see whether they were correct and move on to the next clue or try again. Therefore, I implemented code so that the clue screen has a live in-app camera (no gallery uploads), sends the captured JPEG with the player's GPS coordinates to POST /plays/{play_id}/clues/{clue_id}/answer, and shows the result in a sheet with the backend's message and the attempt count, for players.

The new pieces are the CameraCapture component, submitAnswer in api/game.js, postForm in api/client.js, and the photo answer flow in ClueView. After a correct answer, the screen loads the next clue, or the finish screen if the play is complete. After a wrong answer, the photo is cleared so the player can retake it.

When I reviewed client.js, I noticed that request() sends Content-Type: application/json on every call, which I had flagged in PR #220. A multipart upload sent with that header has no boundary, so FastAPI cannot read the image. Therefore, I added postForm, which passes empty headers so the browser sets the multipart Content-Type with its boundary itself.

When I reviewed CameraCapture.vue, I noticed that the camera would stay on after the photo was taken or the player left the screen, and that each preview created an object URL that was never released. Therefore, I stop every track in the stream when a photo is captured and on unmount, and revoke the preview URL whenever the photo changes and on unmount.

When I reviewed the error handling in ClueView, I noticed that location errors and backend errors both landed in the same catch, so a player who denied location access would see a generic message. Therefore, submitErrorMessage checks the geolocation error code first (permission denied gets its own message), and otherwise shows the backend's detail.

When I reviewed the submit flow, I noticed that if the clue had already been answered (for example in another tab), the backend returns 409 and the player would be stuck on a clue they cannot answer. Therefore, on a 409 the screen clears the photo and reloads the play state so it jumps to the current clue.

When I tested the flow by hand, I noticed that the clue audio is still a placeholder, so a tester has no way to know which room sign to photograph. Therefore, I added a development-only endpoint, GET /dev/clues/{clue_id}/room, and the placeholder shows "Test mode · Room ..." when it responds.

The PR contains one temporary testing helper, the /dev clue room endpoint and its display in ClueAudioPlaceholder. It is only registered when the backend runs with ENV=development, so it never exists in production, and the placeholder shows nothing when the endpoint is missing. It is marked with a TODO to delete ClueAudioPlaceholder.vue, routers/dev_router.py and its block in main.py in the audio PR. The rest of the PR calls the real answer endpoint with no stubbed values.

The PR only contains small functions, none longer than 25 lines.

I read the full diff line by line and searched the changed files for duplicated blocks, unused imports and magic numbers to ensure that my feature contribution does not contain any of the following:

hardcoded values (the only literals are the camera hints, back camera and ideal 1920x1080, and the JPEG quality of 0.9, each used once where it applies)
duplicate code (the result sheet reuses the existing badge animation and SVG styles from the finish screen)
dead code
unnecessary function calls
excessive conditional logic (the camera uses a single status value, idle, starting, live or captured, instead of separate flags)
deep nesting
high cyclomatic complexity
classes/modules/functions with many unrelated responsibilities (CameraCapture only produces a photo through v-model, the API files only build requests, and ClueView only connects them)

This work is written in the new components/CameraCapture.vue and in the existing views/ClueView.vue, api/game.js and api/client.js because the camera is a reusable component that only knows about taking a photo, the API calls stay in the api layer with the other game requests, and the view coordinates the clue screen as it already did. The testing helper is in the new routers/dev_router.py so it can be registered or left out as a whole.

This work belongs in process 4, "Evaluate photo", in the game loop level 1 DFD because it is where the player's photo enters the system and where the correct or retry result comes back to the player.

Testing receipts for PR #251

The functionality works correctly because the happy path tests "sends the photo and location for the current clue to the checker", "moves on to the next clue after a correct answer", "shows the finish screen after the last correct answer", "takes a JPEG photo, shows it and turns the camera off", "submitAnswer() sends the photo and coordinates as form data", "postForm() sends FormData and lets the browser set the content type" and test_get_clue_room_returns_the_clue_target_name passed.

I wrote tests to cover abnormal situations involving a wrong answer that lets the player try again, a clue that was already answered (409 reloads the play), the shutter staying disabled until the camera is live, Submit staying disabled until a photo is taken, the Checking state while the answer is checked, retaking a photo, the camera turning off when the component goes away, and the test room only showing in development, and they passed.

I checked that these negative cases involving blocked camera access, a browser with no camera access over http, denied location access, a photo rejected by the backend, a missing clue on the dev endpoint (test_get_clue_room_404s_for_missing_clue) and the dev endpoint being absent outside development failed as expected, showing the matching error message or a 404 and no test room.

When I reviewed the ClueView tests, I noticed that mounting the real CameraCapture would need a camera and a playing video in jsdom. Therefore, I stubbed it with a button that emits a photo, since the camera itself is covered by its own tests.

When I reviewed the ClueView tests, I noticed that ClueAudioPlaceholder now calls the dev endpoint on mount, so every ClueView test made an extra unmocked request. Therefore, I mocked api/client to reject that call, which matches running outside development.

When I reviewed the CameraCapture tests, I added "has no way to upload a file" to check that the component has no file input, since the design requires in-app capture only.

Among these tests, the CameraCapture, ClueAudioPlaceholder, ClueView, client and game tests are unit tests, and test_get_clue_room_returns_the_clue_target_name and test_get_clue_room_404s_for_missing_clue are integration tests because they call the router through TestClient against the in-memory database and the real target repository.

These tests are included in the directories tests/frontend/components/CameraCapture.test.js, tests/frontend/components/ClueAudioPlaceholder.test.js, tests/frontend/views/ClueView.test.js, tests/frontend/api/client.test.js, tests/frontend/api/game.test.js and tests/backend/test_routers/test_dev_router.py.

This new test PR did not break anything else in the system because, after main (including the role changes from PR #250) was merged into the branch, I ran the full frontend suite with npm test and the full backend suite with pytest, and all tests passed.