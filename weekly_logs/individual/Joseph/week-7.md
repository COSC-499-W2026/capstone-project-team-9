## For PR #148: Game options endpoints

Requirement: Custom Game Creation (#81)

As part of requirement Custom Game Creation, the user needs to open the game setup screen, see the available languages, difficulties and game lengths, and choose one of each (length with a slider). Therefore, I implemented/generated code so that any user creating a game can fetch the list of languages (GET /languages), the list of difficulties (GET /difficulties), and the minimum and maximum game length (GET /game-lengths).

Code review

When I reviewed the first version of game_options_service.py, I noticed it exposed game length as a fixed list of options (5, 10, 15). That doesn’t match the slider design the team chose, which needs a minimum and maximum. Therefore, I changed it to a {min, max} range (MIN_GAME_LENGTH, MAX_GAME_LENGTH) and updated the endpoint, schema and tests.

When I tested GET /difficulties by hand, it returned a 500. The backend log showed that the difficulty table didn’t exist, because init_db.py only runs when it’s run manually. Therefore, I ran init_db.py to create the table, and all three endpoints then worked. [note to teammates / README if you add one]

For the rest of the generated code, I did not find any problems with it because I checked each endpoint in the /docs page, confirmed the empty-table and populated-table responses, and ran the full test suite.

Temporary workaround: This PR contains one temporary item: the game length range is two hardcoded constants with a TODO to confirm the maximum with the client or decide as a team. Everything else is the long-term design. The constants live in one place and the frontend reads them from the endpoint, so changing them is a one-line edit.

Small functions: The PR only contains small functions that are at most about 5 lines long.

Code quality: By searching the diff for literal numbers and repeated logic, I found that my feature contribution contained hardcoded values (the length range). Therefore, I made them named constants in game_options_service.py and exposed them via the endpoint so nothing else hardcodes them. Now, I can confirm that my feature contribution does not contain duplicate code, dead code, unnecessary function calls, excessive conditional logic, deep nesting, high cyclomatic complexity, or classes/modules/functions with many unrelated responsibilities.

Architecture: This work is written in game_options_router.py, game_options_service.py and game_options_repo.py because the project separates HTTP handling (router), process logic (service) and database access (repository), and the repo has a get_session dependency in core/db.py for the database session. This work belongs in the [name of the start game / game loop process] in the level 1 game loop DFD, because it supplies the choices a player makes before a game starts.



### Testing receipts (same PR #148)

The functionality works correctly because the happy path tests involving languages returned sorted by name, difficulties returned in id order, languages and difficulties found by id, the three endpoints returning the right data, and /game-lengths returning {min, max} all passed. I wrote tests to cover abnormal situations involving empty language and difficulty tables (the endpoints return []) and they passed. I checked that these negative cases involving looking up a language or difficulty id that doesn’t exist (returns None) failed as expected, because that is how the service detects an invalid choice in the next PR.

When I reviewed the generated tests, I did not find any problems with them.

Among these tests, the tests in test_game_options_repo.py are unit tests and the tests in test_game_options_router.py are integration tests (router, service, repo and an in-memory SQLite database together). difficulty was also added to the expected tables in test_model_registration.py.

These tests are included in the directory tests/backend/.

This new test PR did not break anything else in the system because I ran the full suite with docker compose exec backend pytest.

## For PR #151: Start a custom game

Requirements: Custom Game Creation (#81) and Start a Play (#82)

As part of requirements Custom Game Creation and Start a Play, the user needs to pick a language, difficulty and length, then ask to start the game, and receive a randomized set of clues for that game. Therefore, I implemented/generated code so that any user creating a custom game can call POST /games, which validates their choices, picks random clues matching the language and difficulty, saves the game, and returns the saved game settings plus the list of clue ids.

Code review

When I reviewed my first design of the response, I noticed it returned only the game’s settings. The issue says one route should both create and start the game and respond with a randomized list of clues. Therefore, I changed the service and response to return the game together with the clue ids.

When I reviewed the first version of start_game, I noticed that saving the game before picking clues would leave a game row behind if there weren’t enough clues. Therefore, I ordered it so that validation and clue selection happen first and the game is only saved when enough clues exist. A test checks that nothing is saved when the request fails.

When I reviewed the response contents, I considered returning targets or audio. I decided against it because a target is the answer, and audio is a large bytea column. Therefore, the response returns clue ids only, and get_random_clue_ids selects only the ids so it never loads the audio.

When I tested POST /games by hand, it returned a 500 because the clue table didn’t exist yet. Therefore, I ran init_db.py to create the new tables, then seeded test clues with a throwaway script, which is not committed.

Temporary workaround: This PR contains temporary items: no Play row is saved yet because Play.user_id is NOT NULL and login doesn’t exist, so only the Game is saved. The creator_id columns on Game, Clue and Target are plain nullable ints instead of foreign keys until the User model exists. Neither changes the response shape when added later.

Small functions: The PR only contains small functions. The longest is start_game at about 20 lines, and _validate_settings and the router function are about 10 lines each.

Code quality: By reviewing the diff for the listed problems, I found that my feature contribution contained duplicate code: the same timestamp helper was defined in each of the Game, Clue and Target models. Therefore, I moved it to a shared utc_now in core/clock.py. I also found hardcoded values and no new ones: the length range comes from the named constants in game_options_service.py and is not repeated. [If you removed Field(gt=0): I also removed the duplicate minimum from the schema so the service owns the range. If you kept it: I kept the schema check, which rejects 0 before the service.] Now, I can confirm that my feature contribution does not contain hardcoded values, duplicate code, dead code, unnecessary function calls, excessive conditional logic, deep nesting, high cyclomatic complexity, or classes/modules/functions with many unrelated responsibilities.

Architecture: This work is written in game_router.py, game_service.py, clue_repo.py and game_repo.py because the router only handles HTTP, the service holds the start-game process (validate, pick clues, save), and the two repositories each own their own table’s queries. This work belongs in the [name of the start game process] in the level 1 game loop DFD, because it takes the player’s settings and produces the game and its clues.



### Testing receipts (same PR #151)

The functionality works correctly because the happy path tests involving starting a game with enough clues, only using clues matching the chosen language and difficulty, starting with exactly enough clues, accepting the maximum length, recording the creator, the repo returning the requested number of distinct ids, and the router returning 201 with the game and clues passed. I wrote tests to cover abnormal situations involving fewer clues available than requested at the repo level and an empty clue table, and they passed. I checked that these negative cases involving an unknown language, an unknown difficulty, a length below the minimum, a length above the maximum, not enough clues (with nothing saved), and malformed request bodies (empty, missing fields, num_clues of 0, non-integer language) failed as expected.

When I reviewed test_start_game_rejects_unavailable_options (the below-minimum case), I noticed it failed because num_clues = 0 was rejected by the schema’s validation before the service ran, so the service’s own check was never reached and the error message didn’t match. Therefore, I changed the test’s settings helper to use model_construct, so the service tests exercise the service’s own validation, and the schema’s rejection of 0 stays covered by the router test.

Among these tests, the tests in test_clue_repo.py and test_game_service.py are unit tests and the tests in test_game_router.py are integration tests. The model registration test now expects the game, target and clue tables too.

These tests are included in the directory tests/backend/.

This new test PR did not break anything else in the system because I ran the full suite with docker compose exec backend pytest and got 82 passed, 1 skipped after the fix.