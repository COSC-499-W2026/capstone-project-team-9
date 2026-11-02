Log 1: Change the answer check to look up the target by clue id

For PR #218:

As part of requirement Evaluate image, the user needs to submit a photo and their location for a clue and find out whether they are at the right room and the photo shows that room's code. Therefore, I implemented code so that verify_answer takes a clue_id, fetches that clue's target through the new target_repo, and checks the player's location and photo against it, for players.

Previously the caller had to supply the expected room code and the target location. Now both come from the target row: name gives the room code, and latitude, longitude and radius give the location.

When I reviewed answer_service.py, I noticed that it imported get_target_by_id through from app.backend.src.repositories.... That path does not exist in the container, where PYTHONPATH=/app/src, and it raised ModuleNotFoundError. Therefore, I changed it to from repositories.target_repo import get_target_by_id.

When I reviewed test_answer_service.py, I noticed that the tests patched services.answer_service.get_clue_target, but the service imports get_target_by_id, so monkeypatch raised AttributeError. Therefore, I changed the patch string to services.answer_service.get_target_by_id.

When I reviewed get_target_by_id, I noticed that its name suggests it takes a target id, but it takes a clue id and joins through Clue. That is easy to misread. Therefore, I kept the name and stated in the docstring that the parameter is a clue id.

The PR does not contain any temporary workaround because the lookup is a single join query with no stubbed values, and the room code and location both come from the target row.

The PR only contains small functions, none longer than 20 lines.

I read the full diff line by line and searched the changed files for duplicated blocks, unused imports and magic numbers to ensure that my feature contribution does not contain any of the following:

hardcoded values (the messages are named constants and the room code comes from the target name)
duplicate code
dead code (I removed the old expected_room and target_location parameters)
unnecessary function calls
excessive conditional logic (three early returns, no nesting)
deep nesting
high cyclomatic complexity
classes/modules/functions with many unrelated responsibilities (_room_code is separate from verify_answer, and the query lives in the repo)

This work is written in services/answer_service.py and the new repositories/target_repo.py because the service holds the correct-or-wrong decision and the repository holds the data access, which keeps the layers separate.

This work belongs in process 4, "Evaluate photo", in the game loop level 1 DFD because it receives the player's photo, reads the expected answer from the Game item DB, and returns the feedback.

Testing receipts for PR #218

The functionality works correctly because the happy path tests test_correct_answer_checks_room_code_from_target_name and test_get_target_by_id_returns_the_clues_target passed.

I wrote tests to cover abnormal situations involving a wrong photo at the right place, a wrong location that skips OCR, a clue id that differs from its target id (test_get_target_by_id_takes_a_clue_id_not_a_target_id), and several clues each resolving to their own target, and they passed.

I checked that these negative cases involving an unknown clue (test_unknown_clue_raises) and a missing clue id (test_get_target_by_id_is_none_for_missing_clue) failed as expected, raising ClueNotFoundError and returning None respectively.

When I reviewed test_get_target_by_id_returns_the_target, I noticed that it created a target with no clue pointing at it, so the join found nothing and the test failed. Therefore, I rewrote the tests to create clues with the add_clues fixture.

When I reviewed the id-matching tests, I noticed that add_clues creates targets and clues in lockstep, so a bug that compared the wrong id would still pass. Therefore, I added a test with an unused target to shift the ids.

Among these tests, all are unit tests, and integration tests are not required because the service tests fake the repo and OCR, the repo tests use the in-memory database, and the HTTP layer is tested separately in PR #220.

These tests are included in the directories tests/backend/test_services/test_answer_service.py and tests/backend/test_repos/test_target_repo.py.

Log 2: Add the answer verification router

For PR #220:

As part of requirements Upload image and Evaluate image, the user needs to take a photo at a clue's location, upload it with their coordinates, and receive a correct or wrong result. Therefore, I implemented code so that POST /answers/verify accepts a clue_id, latitude, longitude and an image file and returns {correct, message}, for players.

The route returns 200 for both correct and wrong answers. It returns 404 for an unknown clue, 422 for an unreadable image or invalid fields, and 413 for images over 10 MB.

When I reviewed answer_router.py, I noticed that async def would let the slow OCR block the event loop. Therefore, I used a plain def so FastAPI runs it in its threadpool.

When I reviewed the image handling, I noticed that reading the whole upload into memory has no limit. Therefore, I read at most MAX_IMAGE_BYTES + 1 bytes and return 413 if the limit is exceeded.

When I reviewed the frontend client, I noticed that client.js sends Content-Type: application/json on every request, which would break multipart uploads. Therefore, I left that change for the frontend PR, since this PR only adds the backend route.

The PR does not contain any temporary workaround because the route calls the real service and repo. The location still comes from the client, which is a known limitation (a player's browser can report a false location) that I am recording rather than working around.

The PR only contains small functions, none longer than 20 lines.

I read the full diff line by line and searched the changed files for duplicated blocks, unused imports and magic numbers to ensure that my feature contribution does not contain any of the following:

hardcoded values (the size limit is the named constant MAX_IMAGE_BYTES)
duplicate code
dead code
unnecessary function calls
excessive conditional logic (the router only maps exceptions to status codes)
deep nesting
high cyclomatic complexity
classes/modules/functions with many unrelated responsibilities (the router does HTTP only, and all decisions are in the service)

This work is written in the new routers/answer_router.py and schemas/answer_schema.py because it follows the existing router, service, repo layering used by location_router and game_router.

This work belongs in process 4, "Evaluate photo", in the game loop level 1 DFD because the router is the entry point where the player's photo arrives and where the Feedback / Error result goes back out.

Testing receipts for PR #220

The functionality works correctly because the happy path tests test_correct_answer and test_wrong_answer_is_still_200 passed.

I wrote tests to cover abnormal situations involving an unknown clue (404), an unreadable image (422), invalid latitude, longitude and clue id values (422), a missing image (422), and an oversized image (413), and they passed.

I checked that these negative cases involving invalid form fields and a missing image failed as expected with 422.

When I reviewed the router tests, I noticed that they patch routers.answer_router.verify_answer, so every test fails if the function is renamed or its import changes. Therefore, I kept the patch string in sync with the import in the router.

When I reviewed coverage of the router, I noticed that there was no test for the 413 oversize path. Therefore, I added test_oversized_image_returns_413.

Among these tests, all are unit tests, and integration tests are not required because the service is faked in the router tests and is covered by its own tests in PR #218.

These tests are included in the directory tests/backend/test_routers/test_answer_router.py.