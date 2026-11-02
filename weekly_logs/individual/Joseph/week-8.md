# Individual Log


## For PR # 210

### Requirement and functionality

As part of requirement **"Custom game creation: the system shall allow any user to create a game with a particular difficulty, language, length"**, the user needs to:

1. Open the game creation screen
2. Pick a language
3. Pick a difficulty
4. See the available game lengths for that combination
5. Choose a length
6. Start the game

Therefore, I implemented code so that players (any user) can request the playable game length range for a chosen language and difficulty. The range reflects how many clues actually exist (e.g. 1 to 6 if French/Medium has 6 clues, capped at 10, and 0 to 0 if the combination has no clues).

This PR does not change the database schema and does not add new user-data validation beyond FastAPI's required integer query parameters, so no Data Modeling receipts apply.

### Code review

- When I reviewed `count_clues` in `clue_repo.py` and `get_game_length_range` in `game_options_service.py` for this functionality, I did not find any problems with it because I checked that the query filters on both `language_id` and `difficulty_id`, that the service caps the result with `MAX_GAME_LENGTH`, and that the zero-clue case returns `(0, 0)` instead of a range starting at 1. Tests for each of these passed.
- When I reviewed the `/game-lengths` endpoint, I noticed the old router test called it with no parameters, which would now fail with a 422 since `language_id` and `difficulty_id` are required. Therefore, I replaced that test with tests that pass the parameters and added a test that missing or invalid parameters return 422.
- When I reviewed the seed data in `seed_dev.py`, I noticed that the `Target` model has no `image` column and requires `latitude`, `longitude` and `radius`, so seeding targets with an image would not insert. Therefore, I seeded placeholder targets with `latitude`, `longitude` and `radius`, and used empty bytes for `Clue.audio` because that column is NOT NULL.

### Workarounds

The PR does not contain any temporary workaround because the range is computed from real clue counts in the database, and `start_game` still re-validates clue availability when a game is created. The only placeholder is the empty audio on seeded dev clues, which is dev-only data behind the `ENV=development` guard.

### Function size

The PR only contains small functions:

- `count_clues`: 4 lines
- `get_game_length_range`: 4 lines
- `get_game_lengths` endpoint: 1 line
- `_seed_fake_clues` (seeding helper): about 22 lines

### Code quality checks

I read through every changed file and searched for repeated logic to ensure that my feature contribution does not contain any of the following:

- hardcoded values
- duplicate code
- dead code
- unnecessary function calls
- excessive conditional logic
- deep nesting
- high cyclomatic complexity
- classes/modules/functions with many unrelated responsibilities

Specifically:

- The length limits are named constants (`MIN_GAME_LENGTH`, `MAX_GAME_LENGTH`).
- The counting query exists once in `clue_repo.py` and is reused by the service.
- Each function has one job (query, business rule, HTTP).
- Nesting is one level deep, and the only branch in the new logic is the zero-clue check.
- The fake clue counts in `seed_dev.py` are intentionally hardcoded dev data kept in a named constant, `FAKE_CLUE_COUNTS`.

### Architecture

- This work is written in `clue_repo.py`, `game_options_service.py` and `game_options_router.py` because of the layered architecture: the repository only talks to the database, the service holds the business rule (the cap and the zero case), and the router only handles HTTP.
- The seed data is written in the existing `seed_dev.py` because it is fake data that must never reach production, and that file already has the `ENV=development` guard.
- This work belongs in the **"Get game options"** process in the DFD (the game creation part of the game loop) because it supplies the options a player chooses from before the **"Start custom game"** process runs.

---

## For test PR # 210 written to assess functionality in PR # 210 (dynamic game length options)

### Test results

- **Happy path:** The functionality works correctly because the happy path tests passed. These covered a clue count below the cap (max equals the count), a clue count above the cap (max equals `MAX_GAME_LENGTH`), counting only the chosen language/difficulty combination, and the endpoint returning the right range for valid parameters.
- **Abnormal situations:** I wrote tests covering a combination with no clues (returns 0 to 0) and clues existing only for other languages or difficulties, and they passed.
- **Negative cases:** I checked that these negative cases failed as expected with a 422 response: missing `language_id`, missing `difficulty_id`, both missing, and a non-integer `language_id`.

### Test review

When I reviewed the old `test_get_game_length_range` in `test_game_options_router.py`, I noticed that it called `/game-lengths` with no query parameters, which no longer matches the endpoint's contract and would fail with a 422. Therefore, I replaced it with tests that send the parameters.

### Unit vs. integration tests

Among these tests:

- `test_clue_repo.py` and `test_game_options_service.py` tests are **unit tests** (each layer is tested alone against an in-memory database).
- `test_game_options_router.py` tests are **integration tests** (they go through the router, service, repository and database together).

### Test locations

- `tests/backend/test_repos/test_clue_repo.py`
- `tests/backend/test_services/test_game_options_service.py`
- `tests/backend/test_routers/test_game_options_router.py`

### Regression testing

This new test PR did not break anything else in the system because I ran the full backend suite with `docker compose exec backend pytest` and every test passed. I also manually checked `/game-lengths` and `POST /games` in the FastAPI docs after running `reset_db.py`, and the results matched the expected ranges and 422 errors. 


## PR # 213: Remove clues from create game

As part of the "Custom game creation" and "Start a Play" requirements, the user needs to choose a language, difficulty and length, create a game, and later start a play of it. Clue selection belongs to the play, not the game. Therefore, I implemented code so that creating a game saves only its ruleset and rejects games that can never be played, for any user creating a custom game.

When I reviewed `create_game` and `_validate_settings` in `game_service.py` for this functionality, I noticed the old `start_game` loaded random clue ids only to compare their count with `num_clues`, then threw the ids away. That does extra database work for no reason. Therefore, I replaced it with the existing `count_clues` query. I also noticed the name `start_game` no longer described what the function does, so I renamed it to `create_game` and removed the `StartedGame` class.

When I reviewed `game_schema.py` and `game_router.py`, I did not find any problems with them because I checked that `ClueResponse` and `GameStartResponse` have no remaining references, and that the router now returns `GameResponse` directly.

The PR does not contain any temporary workaround because it only removes behavior and reuses `count_clues` and the existing validation. `creator_id` stays `None` as it did before this PR.

The PR only contains small functions that are at most 15 lines long.

I searched the diff for the following and did a line-by-line read of `game_service.py`, `game_router.py` and `game_schema.py` to ensure that my feature contribution does not contain any of the following:
- hardcoded values (length limits come from `MIN_GAME_LENGTH` and `MAX_GAME_LENGTH`)
- duplicate code
- dead code (I confirmed no leftover imports; `get_random_clue_ids` is intentionally kept because the start-play PR uses it)
- unnecessary function calls (this is why I swapped to `count_clues`)
- excessive conditional logic
- deep nesting
- high cyclomatic complexity
- classes/modules/functions with many unrelated responsibilities

This work is written in the existing files `game_service.py`, `game_router.py` and `game_schema.py` because they already own the game-creation layers (router, service, schema).

This work belongs in the existing "Create custom game" process in the game loop DFD, which now only validates and saves the game settings.

### Testing receipts for PR # 213

The functionality works correctly because the happy path tests involving creating a game with enough clues, creating with exactly enough clues, creating at the maximum length, recording a creator id, and the router returning 201 with game settings and no `clues` key passed.

I wrote tests to cover abnormal situations involving unknown language, unknown difficulty, game length below the minimum and above the maximum, a malformed request body, and clues that exist only for a different language, and they passed.

I checked that these negative cases involving too few clues and invalid settings raise `ValueError` (422 at the router) and save no game, and they failed as expected.

When I reviewed the test `test_create_game_only_counts_clues_for_the_chosen_language_and_difficulty`, I noticed the old equivalent asserted on returned clue ids, which no longer exist. Therefore, I rewrote it to assert that clues from other languages do not count toward the total.

Among these tests, the service tests in `test_game_service.py` are unit tests and the tests in `test_game_router.py` are integration tests.

These tests are included in the directories `tests/backend/test_services/` and `tests/backend/test_routers/`.

This test PR did not break anything else in the system because I ran the full backend suite with `docker compose exec backend pytest` and all tests passed.

---

## PR # 216: Add Play model and PlayClue table

As part of the "Start a Play", "Save game state" and "Pause/Continue Play" requirements, the user needs to start a play, answer clues in order, and later refresh or pause and resume at the same clue. Therefore, I implemented code so that the server stores which clues belong to a play, their order, and which are solved, for any player.

When I reviewed the `Play` and `PlayClue` models for this functionality, I did not find any problems with the table design because I compared both models field by field against the planned columns and constraints, checked the composite primary key, the foreign keys and the `ON DELETE` behavior, and confirmed the unique constraint on `(play_id, position)` in a test.

### Data modeling

This PR changes the database, so the receipts are as follows. I replaced `SolvedClue` with `PlayClue` because `SolvedClue` only recorded solved clues and could not rebuild the plan after a refresh or pause. I updated `schema.sql` and `drawdb-visual-schema.json` to match the models, and made `Play.user_id` nullable because login does not exist yet.

The PR contains one temporary workaround: `Play.user_id` is nullable until login exists. It follows the existing `creator_id` pattern on `Game`, `Clue` and `Target`, and a comment in the model says to make it required once login lands.

The PR only contains small functions; it contains no functions, only two model classes of about 10 lines each.

I compared the models against each other and against the existing models, and searched for repeated definitions to ensure that my feature contribution does not contain any of the following:
- hardcoded values
- duplicate code
- dead code
- unnecessary function calls
- excessive conditional logic
- deep nesting
- high cyclomatic complexity
- classes/modules/functions with many unrelated responsibilities

This work is written in the new files `play_model.py` and `play_clue_model.py` because the project keeps one table model per file in `models/`, and both are registered in `models/__init__.py`.

This work belongs in the data store used by the "Start play" and "Play game" processes in the game loop DFD, since these tables hold play state.

### Testing receipts for PR # 216

The functionality works correctly because the happy path tests involving a play receiving default values (id, `started_at`, no score) and a `PlayClue` starting unsolved with zero attempts passed, along with the registration test for the new tables.

I wrote tests to cover abnormal situations involving two clues sharing the same position in one play, and they passed.

I checked that this negative case involving a duplicate `(play_id, position)` raises `IntegrityError`, and it failed as expected.

When I reviewed the updated `EXPECTED_TABLES` in `test_model_registration.py`, I noticed that my edit used `play_clue` while SQLModel registers the table as `playclue`, which made the test fail. Therefore, I changed it back to `playclue`.

Among these tests, all are unit tests and integration tests are not required because the models are plain data definitions with no logic spanning multiple modules; they are tested against an in-memory SQLite database.

These tests are included in the directory `tests/backend/test_models/`.

This test PR did not break anything else in the system because I ran the full backend suite with `docker compose exec backend pytest` and all tests passed.

---

## PR # 221: Add start play endpoint

As part of the "Start a Play" requirement (the system shall generate an instance of a game, selecting a random combination of clues that match the game's ruleset), the user needs to pick a game, press start, and receive the play with its clues in the order they will be presented. Therefore, I implemented code so that `POST /games/{game_id}/plays` creates a play, picks random clues matching the game's language and difficulty, saves them in order, and returns the play and the clue ids, for any player.

When I reviewed `start_play` in `play_service.py` and `add_play_with_clues` in `play_repo.py` for this functionality, I did not find any problems with them because I walked through each branch (missing game, too few clues, success), confirmed that nothing is saved on either error path, confirmed the play and all its `PlayClue` rows are written in a single commit, and manually ran `reset_db.py`, then `POST /games` and `POST /games/1/plays` in `/docs`, and checked the `playclue` rows in Postgres, which matched the API response order.

When I reviewed the router error handling, I noticed that a missing game and too few clues could both be reported as `ValueError`, which would make the router return the same status code for two different situations. Therefore, I made `GameNotFoundError` a separate exception that does not subclass `ValueError`, so the router returns 404 for a missing game and 422 for too few clues.

The PR contains one temporary workaround: `start_play` is called without a user id, so plays are anonymous until login exists. This matches the nullable `user_id` from the previous PR and the way `creator_id` is handled, and the router will pass the user id once auth lands.

The PR only contains small functions that are at most 15 lines long.

I did a line-by-line read of the new files and searched for repeated logic to ensure that my feature contribution does not contain any of the following:
- hardcoded values (clue counts come from the game, and no ids are hardcoded)
- duplicate code (random selection reuses the existing `get_random_clue_ids`)
- dead code (`get_random_clue_ids` is now used again)
- unnecessary function calls
- excessive conditional logic
- deep nesting
- high cyclomatic complexity
- classes/modules/functions with many unrelated responsibilities (the router handles HTTP, the service holds the rules, and the repo handles saving)

This work is written in the new files `play_router.py`, `play_service.py`, `play_repo.py` and `play_schema.py`, plus the existing `game_repo.py` for `get_game`, because the project separates routers, services, repositories and schemas by layer, and plays are a separate concern from games.

This work belongs in the "Start play" process in the game loop DFD, which reads the Game, Clue and Difficulty/Language data and writes to the Play and PlayClue data stores.

### Testing receipts for PR # 221

The functionality works correctly because the happy path tests involving starting a play for an existing game, returning the requested number of distinct clues, saving clues in the returned order with positions 1 to N, using only clues that match the game's language and difficulty, working with exactly enough clues, recording the user id when given, and the router returning 201 with the play and ordered clues passed.

I wrote tests to cover abnormal situations involving a non-integer game id, a user id left as `None`, and clues existing only for other languages or difficulties, and they passed.

I checked that these negative cases involving an unknown game (404) and too few clues (422) save no play and no `PlayClue` rows, and they failed as expected.

When I reviewed the test `test_start_play_raises_when_not_enough_clues_and_saves_nothing`, I noticed it only checked that no `Play` was saved, so orphaned `PlayClue` rows could go unnoticed. Therefore, I added an assertion that the `PlayClue` table is also empty.

Among these tests, the tests in `test_game_repo.py`, `test_play_repo.py` and `test_play_service.py` are unit tests and the tests in `test_play_router.py` are integration tests.

These tests are included in the directories `tests/backend/test_repos/`, `tests/backend/test_services/` and `tests/backend/test_routers/`.

This test PR did not break anything else in the system because I ran the full backend suite with `docker compose exec backend pytest` and all tests passed.