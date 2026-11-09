# Individual Log: Joseph Mondelli

---

## PR # 233: Add `GET /plays/{play_id}` to report play progress

As part of requirement **Save game state** (the system shall save an in-progress play's current state, so the user can pause or disconnect) and the related requirements **Pause Play** and **Continue Play**, the user needs to do the following in the system: start a play, leave or refresh the page, and then return and see where they are in the round. Therefore, I implemented/generated code (with AI assistance) so that the frontend, used by players, can call `GET /plays/{play_id}` and receive the play's `current_clue_id`, `total_clues`, `solved_clues` and whether the play is `completed`. It returns 404 for a play that doesn't exist.

**Data modeling:** this PR changes the database by adding a nullable `completed_at` timestamp (with timezone) column to `Play`. A play is in progress while it is null. I updated the `Play` model, `schema.sql` and `drawdb-visual-schema.json` together so the three stay consistent. The column is nullable because existing and in-progress plays have no completion time. Because `create_all` doesn't alter existing tables, the PR notes tell teammates to run `reset_db.py`. The only user input is the `play_id` path parameter, which FastAPI validates as an integer (a non-integer returns 422).

When I reviewed the `get_play_state` service method and the router endpoint for this functionality, I noticed that the first version returned a full list of every clue in the play. This is problematic because the frontend only needs the next clue and progress, and my team had already objected to returning a clue list from the start-play endpoint. Therefore, I replaced the list with `current_clue_id`, `total_clues` and `solved_clues`, and updated the schema, router and tests.

When I reviewed `get_play_clues` in `play_repo.py` (the repository function that loads the clues in position order) after adding it, I noticed that 9 tests failed with `TypeError: 'module' object is not callable`. The cause was that `select` referred to Python's built-in `select` module instead of SQLModel's `select()`, which is a problem because every query using it crashes. Therefore, I fixed the import to `from sqlmodel import Session, select` and removed the stray import. Pytest then showed the failures were gone.

When I reviewed the router test `test_get_play_returns_state_with_ordered_clues`, I noticed that the first draft started a second play to get the clue ids, so it asserted against the wrong play, and that pasting both drafts would have created two functions with the same name where the second silently overrides the first. Therefore, I deleted the broken draft and kept the version that reads the clue ids from the same play it queries.

The review by Ian identified that the logic for `current_clue_id`, `total_clues` and `solved_clues` was implemented as properties on `PlayState` instead of in the play repository. This was inconsistent with the existing pattern where counting queries live in the repo (like `ClueRepository.count_clues`), and PR 2 needed the same "unsolved" logic. Therefore, I moved them into three repository functions (`count_play_clues`, `count_solved_play_clues`, `get_current_clue_id`), made `PlayState` a plain dataclass of values, and had `get_play_state` call the repo. I deleted `get_play_clues` and its three tests since they became dead code, and added repo tests for the new functions. One service test then failed with `AttributeError: 'PlayState' object has no attribute 'clues'` because it asserted on `state.clues`. I removed that assertion, since clue ordering is now covered by the repo tests.

The PR does not contain any temporary workaround because the feature is a complete, long-term read-only endpoint. `completed_at` is never set in this PR, but that is deliberate staging, because setting it belongs to the answer endpoint in the next PR and no code here fakes or hardcodes a value for it.

The PR only contains small functions that are at most 14 lines long (the longest is the router endpoint; the repo functions are 1 to 7 lines each).

I did the following to ensure that my feature contribution does not contain any of the following:
- hardcoded values
- duplicate code
- dead code
- unnecessary function calls
- excessive conditional logic
- deep nesting
- high cyclomatic complexity
- classes/modules/functions with many unrelated responsibilities

Specifically, I read through the diff looking for each item, checked that no literal ids, magic numbers or copied query logic were present (the "unsolved" rule is defined once, in the repo), and checked that every function is called somewhere. This process found dead code: after the refactor, `get_play_clues` and the `PlayClue` import in `play_service.py` were unused. Therefore, I deleted them along with their tests. Now, I can confirm that my feature contribution does not contain any of the items in the list above. The functions have at most one conditional and no nesting.

This work is written in the existing `play_model.py`, `play_repo.py`, `play_service.py`, `play_schema.py` and `play_router.py` because the project's architecture separates layers: database access in repositories, rules in services, data shapes in schemas and HTTP handling in routers. All of it is about plays, so it extends the existing play files instead of creating new ones.

This work belongs in a new read-only "Get play state" process under the game loop in the DFD, which reads from the Play and PlayClue data stores, because it only reports progress and changes no data.

### Testing receipts

For test PR # 233:

The functionality works correctly because the happy path tests involving `get_play` finding an existing play, `count_play_clues` counting only the requested play, `count_solved_play_clues` counting only solved clues, `get_current_clue_id` returning the first position when nothing is solved, skipping solved clues, and returning the lowest unsolved clue, the service tests for current clue and counts, and the router test returning the full progress body and the next clue after one is solved all passed.

I wrote tests to cover abnormal situations involving clues inserted out of position order, clues solved out of order, a play where every clue is solved (`current_clue_id` is `None`), and rows belonging to other plays, and they passed.

I checked that these negative cases involving an unknown play id (service raises `PlayNotFoundError`, router returns 404), a non-integer play id (router returns 422), `get_play` with a missing id, and `count_play_clues` for an unknown play (returns 0) were rejected or returned empty results as expected.

When I reviewed `test_get_play_returns_state_with_ordered_clues`, I noticed the duplicate-draft problem described above. Therefore, I kept only the correct version.

Among these tests, the repo tests (`test_get_play_found_and_missing`, the `count_play_clues` tests, the `count_solved_play_clues` tests and the `get_current_clue_id` tests) are unit tests, and the `get_play_state` service tests and the `GET /plays/{play_id}` router tests are integration tests, because they run the service, repository and an in-memory database together, and the router tests also run the HTTP layer.

These tests are included in the directories `tests/backend/test_repos/test_play_repo.py`, `tests/backend/test_services/test_play_service.py`, `tests/backend/test_routers/test_play_router.py` and `tests/backend/test_models/test_play_models.py` (one assertion that `completed_at` defaults to None). I also added a `solve_clue` fixture to `tests/backend/conftest.py`.

This new test PR broke one existing test, `test_get_play_state_current_clue_is_first_when_nothing_solved`, because it asserted on `state.clues`, which no longer exists after the refactor into repo functions. Therefore, I removed that assertion, since the clue ordering it checked is now covered by the repo tests. Now, I can confirm that this test PR no longer breaks anything else in the system because I reran the full backend suite with `docker compose exec backend pytest` and it finished with 182 passed and 1 skipped (the skipped test is the existing real-photo OCR test that needs sample photos).

---

## PR # 236: Record answers against a play and complete rounds

As part of requirements **Save game state**, **Evaluate image**, **Location check**, and **Skipping and multiple attempts** (the system allows the user to make multiple attempts), the user needs to do the following in the system: get the current clue of their play, go to the room, take a photo of the room code, submit it with their location, find out whether it was correct, and continue to the next clue until the last clue completes the round. Therefore, I implemented/generated code (with AI assistance) so that players can call `POST /plays/{play_id}/clues/{clue_id}/answer` with an image, latitude and longitude. The endpoint checks the location and photo against the clue's target, records the attempt on the `PlayClue` row, marks the clue solved when the answer is correct, and sets `completed_at` on the play when the last clue is solved. It replaces the old stateless `POST /answers/verify`.

**Data modeling:** this PR changes no tables or columns, since `completed_at` was added in the previous PR. It writes to `PlayClue.attempts`, `PlayClue.solved_at` and `Play.completed_at`. It validates user data at the router: `latitude` must be between -90 and 90, `longitude` between -180 and 180, the image is required and capped at 10 MB (413 if larger), and `play_id` and `clue_id` must be integers (422 if not). The service validates that the play exists, that the clue belongs to the play, that it isn't already solved, and that it is the play's current clue. An unreadable image is rejected before anything is written, so it doesn't count as an attempt.

When I reviewed `submit_answer` in `play_service.py` and the new answer router for this functionality, I noticed that while testing by hand in Swagger with a game made of clues 21 and 22, I could submit a correct answer for clue 22 while clue 21 was still the current clue, and it was accepted. This is problematic because a buggy or modified client could solve clues out of order, which makes `current_clue_id` meaningless and would complicate hints, skipping and scoring. Therefore, I added a `ClueNotCurrentError` raised when the submitted clue is not `get_current_clue_id`, mapped it to 409 in the router, placed the check after the already-solved check so a resubmitted solved clue still reports "already solved", and added service and router tests. I also deleted `test_submit_answer_completes_only_when_every_clue_is_solved_in_any_order` because it contradicted the new rule, and `test_submit_answer_solving_last_clue_completes_the_play` still covers completion.

When I reviewed `answer_service.py`, which this feature reuses, I noticed that `Session` was imported from `requests` instead of `sqlmodel`. This is problematic because it is the wrong library, and it only worked because it was used purely as a type hint. Therefore, I changed it to `from sqlmodel import Session`.

The PR does not contain any temporary workaround because the answer flow is the intended long-term design. It reuses `verify_answer` for the OCR and location checks, and it reuses `get_current_clue_id` from the previous PR to decide both which clue is current and when the play is complete, so "solved" is defined in one place. One known limitation is that `record_attempt` and `mark_play_complete` each commit, so a crash between them on the final clue would leave that clue solved with no `completed_at`. This matches how the other repo functions commit and is documented in the PR notes as a possible follow-up. `Play.user_id` is still null because login isn't connected to plays yet, which is existing behaviour and not something this PR introduces.

The PR only contains small functions that are at most 20 lines long (the longest are the `submit_answer` router endpoint and `PlayService.submit_answer`; the repo functions are 3 to 8 lines each).

I did the following to ensure that my feature contribution does not contain any of the following:
- hardcoded values
- duplicate code
- dead code
- unnecessary function calls
- excessive conditional logic
- deep nesting
- high cyclomatic complexity
- classes/modules/functions with many unrelated responsibilities

Specifically, I read through the diff for each item. There are no literal ids or messages duplicated from other modules (the message constants and `MAX_IMAGE_BYTES` are reused). The OCR and location logic is called from `answer_service` and not copied into `play_service`. The old `/answers/verify` route and its tests were removed instead of left as dead code. `submit_answer` uses flat guard clauses with no nesting, and each of the four checks maps to a distinct error. Responsibilities stay separated: the repo reads and writes rows, the service coordinates the rules, and the router only handles HTTP. This process found no additional problems beyond the ones listed above. Now, I can confirm that my feature contribution does not contain any of the items in the list above.

This work is written in the existing `play_repo.py` and `play_service.py` because it coordinates play progress and persists to the Play and PlayClue tables, in the existing `answer_router.py` (rewritten for the new route) so `main.py` still registers it, in the new `answer_schema.py` for the response shape, and in `answer_service.py` only for the import fix, because the OCR and location checks belong there and are reused unchanged.

This work belongs in a "Submit answer" process in the DFD, under the game loop, which now writes to the Play and PlayClue data stores and reuses the existing "Verify location" and "Check photo" processes, because recording progress is part of the play flow and the checks stay where they were.

### Testing receipts

For test PR # 236:

The functionality works correctly because the happy path tests involving a correct answer solving the clue, `record_attempt` counting and solving, attempts accumulating across tries, solving clues in order completing the play on the last one, and the router returning 200 with the recorded result and `play_complete: true` passed. I also ran the flow by hand in Swagger with a game of 2 Easy French clues, and confirmed in the database that `attempts` and `solved_at` were set on each `PlayClue` and `completed_at` on the `Play`.

I wrote tests to cover abnormal situations involving a wrong answer counting an attempt without solving, a wrong answer on the last clue not completing the play, wrong answers followed by a correct one, and an attempt on one clue not touching another clue, and they passed.

I checked that these negative cases involving an unknown play (404), a clue not in the play (404), an already solved clue (409), a clue that is not the current clue (409, with no OCR call and nothing recorded), an unreadable image (422, nothing recorded), an oversized image (413), out-of-range latitude or longitude (422), a missing image (422) and non-integer ids (422) were rejected as expected.

When I reviewed `test_submit_answer_completes_only_when_every_clue_is_solved_in_any_order`, I noticed that it solved the clues in an order the server now rejects, so it tested behaviour that is no longer valid. Therefore, I deleted it and kept the in-order completion test.

Among these tests, the repo tests (`get_play_clue` found, missing and scoped to its play; `record_attempt` for wrong, correct, accumulating and isolated cases; `mark_play_complete`) are unit tests, and the `submit_answer` service tests and the answer router tests are integration tests, because they run the service, repository and in-memory database together (with OCR and location faked so tests are fast), and the router tests also run the HTTP layer and form parsing.

These tests are included in the directories `tests/backend/test_repos/test_play_repo.py`, `tests/backend/test_services/test_play_service.py` and `tests/backend/test_routers/test_answer_router.py` (rewritten for the new route).

This new test PR broke the old router tests for `POST /answers/verify` because the route was replaced and `clue_id` moved from the form body into the URL. Therefore, I replaced that test file with tests for the new route, covering the same cases (correct, wrong, unknown clue, unreadable image, invalid fields, missing image) plus the new ones. Now, I can confirm that this test PR no longer breaks anything else in the system because I reran the full backend suite with `docker compose exec backend pytest` and it passes.