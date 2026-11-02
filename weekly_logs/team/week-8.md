# Team 9 (The ENJIneers): Week 8 Team Log

Eric Villeneuve, Nash Lovegren, Joseph Mondelli, Ian Steyn

## Goal and work distribution

This week, we decided to focus on , getting the basic structures of the core game in place: the requirements Sign-up, Log-in, Custom game creation, Start a Play, Location check, Upload image and Evaluate image. Our goal was a tested backend for the core game loop (create a game, start a play with ordered clues, and verify a player's photo and location against a clue's target), working login and registration from the frontend to the backend, and a cleaner layered architecture so the next features are easier to add.

The work was distributed so that Joseph focused on game creation and play setup (PR #210 game length options, PR #213 removing clue selection from game creation, PR #216 the Play and PlayClue tables, PR #221 the start play endpoint). Eric focused on answer checking (PR #218 looking up a clue's target for `verify_answer`, PR #220 the `POST /answers/verify` route with image upload and size limit). Nash focused on user accounts (the login service, schema and `POST /login` router with tests, plus the Register and Login views in the Vue frontend with their tests and API client tests). Ian focused on shared structure (reworking the target and location models into `LocationPoint` and `LocationArea` with seed targets for real campus rooms, introducing dependency injection through `core/dependencies.py`, and adding `BaseRepository`).

We considered alternative workload distributions such as everyone working across all task areas at once, which Joseph suggested in Week 6, and splitting work by layer (one person doing all routers, another all services). We did not go with them because splitting by feature area let each person own a vertical slice from router to database, which kept PRs small and focused, reduced merge conflicts, and matched the focused-areas compromise we agreed on in Week 6.

Based on the merged PRs and test results, we met this goal because all 12 PRs from this week were completed with tests. Each person ran the backend suite in Docker (`docker compose exec backend pytest`) and the tests passed, and the CI workflow runs both backend and frontend tests on every pull request. The endpoints for creating a game, starting a play, verifying an answer, registering and logging in all exist and are covered by router, service and repository tests, and the frontend has working Login and Register views. Scoring and the frontend screens for game creation and photo upload are not built yet, and are planned for next week (see the architecture section for the other follow-up work).

## Code quality

By reviewing each other's pull requests and by doing a line-by-line read of each diff, searching for duplicated blocks and counting the files touched by each change, the team found two of the problems on our list. While reworking the target model, Ian found that the code base contained many dependencies between modules and that changes in one component required changes elsewhere: a small change to the target model forced edits across many different files and layers, and unrelated tests broke because they built their own copies of model shapes. Therefore, Ian introduced dependency injection in `core/dependencies.py` (`SessionDep`, `ClueRepositoryDep`, `GameServiceDep`), added a `BaseRepository` class, and converted `ClueRepository`, `GameService` and `GameOptionsService` to classes so that each layer depends only on the layer directly below it. Ian also found similar logic implemented multiple times, because a separate `TargetLocation` dataclass duplicated what the target model already held. Therefore, he removed it and replaced all of its uses with the shared `LocationArea` model. Joseph also found unnecessary repeated work: `start_game` loaded random clue ids only to count them, so he replaced it with the existing `count_clues` query and renamed it `create_game`, and the start play endpoint reuses `get_random_clue_ids` instead of adding new selection logic. Eric made `answer_service` read both the room code and the location from the single target row instead of having callers pass them in.

Now, the team can confirm that the code in this week's merged work does not contain any of the following:

- similar logic implemented multiple times
- many dependencies between modules
- changes in one component require changes elsewhere

The dependency injection conversion is intentionally partial: `GameService` and `GameOptionsService` still also take the session directly, and the other repositories and services are still plain functions. Converting them is planned for next week, along with changing tests to mock dependencies instead of importing them.

## Data flow diagram

With everyone's newly merged work for this week, the system DFD looks the same as before. No changes to the diagram were needed because this week's work fits into processes and data stores that already exist:

- "Create custom game" and "Get game options" (Joseph, PR #210 and #213) are the game creation part of the game loop. They only validate and save the game ruleset and supply the available game lengths.
- "Start play" (Joseph, PR #216 and #221) reads the Game, Clue, Language and Difficulty data and writes to the Play data store. The new PlayClue table is part of that same store.
- "Evaluate photo" (Eric, PR #218 and #220) receives the player's photo and location, reads the expected answer from the Game item data, and returns feedback or an error.
- The login process (Nash) receives an email and password, reads the User data store and returns user information or an error.

We considered alternative data flows such as choosing the clues when the game is created, which we rejected because a game is only a ruleset and every play should get a fresh random selection. We considered comparing the photo to a stored target image with image processing, which we rejected for now because the OCR room-code check with a location check is simpler and does not need stored images. We considered verifying location on the server from something other than client-reported coordinates, but there is no reliable server-side source, so we recorded the limitation that a browser can report a false location instead.

## Architecture diagram

With everyone's newly merged work for this week, the system architecture diagram looks the same as before. No changes were needed because the new work follows the existing router, service, repository layering and adds no new kind of component. The new login, play and answer routers, services and repositories sit in the same layers as the existing ones. The dependency injection module and `BaseRepository` change how objects in those layers are created and connected, not which layers exist or which direction they depend on. The new Play and PlayClue tables live in the existing database, and the Login and Register views are part of the existing Vue frontend.

We considered alternative architectural components, such as making routers classes, which we rejected because each route only needs to depend on a service and a class adds nothing. We considered a separate service just for target and location logic, but kept it inside the existing location and answer services to avoid a new module for a small amount of code. We considered alternative dependencies, such as continuing to pass the session down from routers through services into repositories. We rejected that because it makes every layer depend on the database and makes unit testing harder. We also considered keeping the model-shape changes local to each module, but sharing `LocationArea` removes duplicated definitions at the cost of a small, deliberate dependency on the models layer.