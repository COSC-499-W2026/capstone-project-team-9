# Week 9 Individual Log
_Ian Steyn_

## For PR [#241 GameRepository & GameOptionsRepository classes](https://github.com/COSC-499-W2026/capstone-project-team-9/pull/241)

> associated issues: 
> - part of [#240 Convert All Repositories to Classes](https://github.com/COSC-499-W2026/capstone-project-team-9/issues/240) (which is itself part of the [#180 dependency injection](https://github.com/COSC-499-W2026/capstone-project-team-9/issues/180) refactor project),

### What I did

As part of our requirement to create a maintainable codebase that can continue to evolve for the rest of our capstone (and be handed off to future teams at the end of it), as well as our requirement to test our code thoroughly and reliably, I am refactoring our codebase so that all repositories and services are classes that use Dependency Injection pattern.

Therefore, in this PR, I implemented code to convert two repositories into classes: `GameRepository` and `GameOptionsRepository`, and injected them as dependencies into all services that use their methods: `GameOptionsService`, `GameService`, and `PlayService`.

### Verification and Problem-solving

TODO
When I reviewed the [reference specific part(s) of generated code] for this functionality, I did not find any problems with it because [explain verification approach taken].  
OR  
When I reviewed the [reference specific part(s) of generated code] for this functionality, I noticed [identify problem details and why it is problematic]. Therefore, I did [explain solution taken].  
(Repeat for additional problems found.)

### Engineering Practices

This PR contains only one known temporary workaround that relates to testing; it is discussed below in Testing Receipts. Otherwise, it moves the codebase closer toward our longterm maintainable solution of defining everything neatly as classes! I am intentionally converting these modules to classes in discrete chunks, so that as little as possible of the codebase is made unavailable to teammates at any given time.

The PR only contains small functions that are 1-3 lines long (there are no new functions except for 3 small pytest fixtures; the short service class constructors were modified sligthtly).

I did the following...
- extended both new repository classes from the existing `BaseRepository` to allow `session` to be used as an instance variable (without having to redeclare identical constructors)
- updated wiring in `core/dependencies.py`, using `Annotated ...Dep` aliases (`GameRepositoryDep` and `GameOptionsRepositoryDep`) to avoid repeating long `= Depends()` expressions
- Ensured that `GameService` and `GameOptionsService` no longer depend directly on `Session` at all, meaning we have clean separation of concerns between layers for those files.
  - (Note: `PlayService` still depends on it, because `play_repository.py` has not yet been converted to a class - followed up in {TODO})
- defined reusable fixtures `game_repo` and `game_options_repo` for testing purposes

... to ensure that my feature contribution does not contain any of the following:
```
 - hardcoded values
 - duplicate code
 - dead code
 - unnecessary function calls
 - excessive conditional logic
 - deep nesting
 - high cyclomatic complexity
 - classes/modules/functions with many unrelated responsibilities
 ```

### Reviews

If applicable: The review by [agent or teammate's name] identified [problem]. Therefore, I did [solution].

### Architecture Impacts

`GameRepository` and `GameOptionsRepository` are written in their existing files (`game_repo.py` and `game_options_repo.py`) because they already own that responsibility, so moving them would only add import and git-history churn.

These classes are exposed at the package level in `repositories/__init__.py`, following Python convention, to make them easier to import.

Dependencies are still defined in one place, `core/dependencies.py`, so that wiring changes happen in one file, and tests can swap implementations via FastAPI's `dependency_overrides`.

As a small portion of a refactor project, this work does not belong in a DFD.

### Testing Receipts

I updated existing tests in the following files, so that all existing tests would pass with the new structure:
- `test_game_options_repo.py`
- `test_game_repo.py`
- `test_game_options_service.py`
- `test_game_service.py`
- `test_play_service.py`

The repo methods are still covered by the existing happy-path tests (e.g. `test_add_game_saves_and_assigns_id`, `test_get_all_languages_returns_them_sorted_by_name`) and edge-case tests (e.g. `test_get_game_found_and_missing`, `test_get_all_languages_empty_table`).

The one testing workaround: the service test fixtures build `GameOptionsService`, `GameService` and `PlayService` with real repositories instead of mocks. Each has a `TODO in future: MOCK these repositories` comment in `test_game_options_service.py`, `test_game_service.py` and `test_play_service.py`. Proper mocking depends on a wider review of how our tests use the database, so it's left for a later PR.

Although our CI workflow is currently down, I can confirm this new test PR did not break anything else in the system because I ran all tests in a fresh Docker container on my machine. My reviewers did the same.  
![Week 9 PR 241 Regression Tests](./pics/week-9-pr-241-tests.png)

---

## For PR [#237 LocationService Class](https://github.com/COSC-499-W2026/capstone-project-team-9/pull/237)

> associated issues: 
> - part of [#239 Convert All Services to Classes](https://github.com/COSC-499-W2026/capstone-project-team-9/issues/239) (which is itself part of the [#180 dependency injection](https://github.com/COSC-499-W2026/capstone-project-team-9/issues/180) refactor project)
> - closes [#209 Combine test_target_location_service and test_location_service](https://github.com/COSC-499-W2026/capstone-project-team-9/issues/209)


### What I did

As part of our requirement to create a maintainable codebase that can continue to evolve for the rest of our capstone (and be handed off to future teams at the end of it), as well as our requirement to test our code thoroughly and reliably, I am refactoring our codebase so that all repositories and services are classes that use Dependency Injection pattern.

Therefore, in this PR, I implemented code to convert the location service into a class `LocationService`, defined it as a dependency in `core/dependencies.py`, and updated the location router and answer service to depend on it.

### Verification and Problem-solving

When I tried to run the app after importing `LocationService` into `answer_service.py`, I noticed that the backend refused to build because dependencies were not resolving correctly. This was because `PlayService` imports the answer service which imports `LocationService`, but `LocationService` was imported _after_ `PlayService` in the package's `__init__.py`. Therefore, I reordered the `services/__init__.py` import statements and added a note on ordering for future reference.

When reviewing the `location_service.py` file, I noticed that the simple `verify_location()` is no longer being used anywhere. I decided that this was ok, since our answer-checking uses a location check now, so being on campus isn't strictly necessary to *start* a game. However, I did not delete the function because we may require it again in the near future.

When I ran the tests for `location_service.py`, most of them failed due to a "too many arguments" error, even though the number of arguments passed in tests was correct. This happened because the `LocationService()` class methods were missing `self` parameters in their declaration, so I added those in - they're needed for class methods even when you don't use `self.` variables directly in a function.

### Engineering Practices

This PR contains only one known temporary workaround: `answer_service.py` is not yet a class, so a `LocationService` object is just instantiated directly inside of `verify_answer()` for now. I did this to avoid cascading refactors affecting too much of the codebase at a time; I am intentionally converting these modules to classes in discrete chunks, so that as little as possible of the codebase is made unavailable to teammates at any given time. Otherwise, the PR moves the codebase closer toward our longterm maintainable solution of defining everything neatly as classes! 

The PR only contains small functions that are 1-4 lines long (there are no new functions except for small pytest fixtures; some existing functions were slightly extended with whitespace for readability).

I did the following...
- defined `LocationService` as a class
- decided `_is_within_radius()` lives outside the class as a module-level helper function, since it is pure math and will never depend on any instance variables
- updated wiring in `core/dependencies.py`, using the alias (`LocationServiceDep`) to avoid repeating long `= Depends()` expressions
- defined reusable fixture `location_service` for testing
- combined existing two test files with related responsibilities (see testing receipts below)

... to ensure that my feature contribution does not contain any of the following:
```
 - hardcoded values
 - duplicate code
 - dead code
 - unnecessary function calls
 - excessive conditional logic
 - deep nesting
 - high cyclomatic complexity
 - classes/modules/functions with many unrelated responsibilities
 ```

### Reviews

TODO: If applicable: The review by [agent or teammate's name] identified [problem]. Therefore, I did [solution].

### Architecture Impacts

`LocationService` is written in the existing file `location_service.py` because it already owned that responsibility. It is exposed at the package level in `services/__init__.py`, following Python convention, to make it easier to import.

Dependencies are still defined in one place, `core/dependencies.py`, so that wiring changes happen in one file, and tests can swap implementations via FastAPI's `dependency_overrides`.

As a small portion of a refactor project, this work does not belong in a DFD.

### Testing Receipts

The functionality works correctly because all existing tests in `tests/backend/test_services/test_location_service.py` pass. I merged the old `test_target_location_service.py` tests into this file, since there was no reason for them to be seperate.

When I reviewed all tests that use the `location_service` fixture (which is new in this PR), I noticed they wouldn't run because the fixture was being passed incorrectly. Therefore, I removed `autouse=true` from the fixture declaration and passed it to each test's header instead.

All existing tests in `tests/backend/test_routers/test_location_router.py` also pass. I modified this file to _**mock and override**_ the location service dependency using `mocker` (instead of faking `verify_location`), so that it actually tests the _unit_ rather than everything that lies underneath.
 - 👉 this is the type of mocking we need to be doing across all of our unit tests, as discussed in PR #241 and issue #243.

Among these tests, all are unit tests.

Although our CI workflow is currently down, I can confirm this new test PR did not break anything else in the system because I ran all tests in a fresh Docker container on my machine. My reviewers did the same.
![Week 9 PR 237 Tests](./pics/week-9-pr-237-tests.png)


---

## For PR [#244 Set up "just"](https://github.com/COSC-499-W2026/capstone-project-team-9/pull/244)

> Associated issues:
> - [#245 Set up aliases for common terminal commands](https://github.com/COSC-499-W2026/capstone-project-team-9/issues/245)

> mini devops PR, template does not apply

This PR sets up a `justfile` so we can alias our common terminal commands with much shorter ones. For example, instead of typing `docker compose exec backend python scripts/reset_db.py`, we can now type `just db-reset`. Running `just` will provide a list of all available recipes.

It also updates our README.md with `just` installation instructions and general improvements to the "Local Development Instructions" section.

---

## For PR [#254 PlayRepository class](https://github.com/COSC-499-W2026/capstone-project-team-9/pull/254)



---

## Non-PR things
- reviews
- project management
- team log