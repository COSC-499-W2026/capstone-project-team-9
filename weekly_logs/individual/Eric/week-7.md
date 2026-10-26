For PR #134:

As part of requirement "Evaluate image" (with "Location check"), the user needs to start a play, hear an audio clue, travel to the building the clue refers to, take a photo and submit it along with their device location. Therefore, I implemented code so that the system can check whether a player's coordinates fall inside the radius of a target's location (latitude, longitude, radius_m) and return allowed/blocked with a message. This supports the student/player user group. Instructors choosing the location on a map is not part of this PR.

Data Modeling receipts: ⚠ this PR adds latitude, longitude and radius_m to the Target table in db/schema.sql (if that change is in #134) and the DB enforces lat/lon ranges and radius_m > 0 with CHECK constraints.

When I reviewed verify_location_with_target and its reuse of is_within_radius for this functionality, I did not find any problems with it because I compared the haversine output against known distances: 0.001° latitude ≈ 111 m matches the test comments, and confirmed the boundary uses <= so a point exactly at the radius is allowed.
The PR does not contain any temporary workaround because the target's location is passed in as a TargetLocation parameter rather than hardcoded, so it works unchanged once a target repository supplies the values. (Unlike verify_location, it does not fetch its own location, since no target repository exists yet.)
The PR only contains small functions that are 5 lines long (verify_location_with_target).
I read the diff line by line against the checklist, searched the repo for other copies of the distance logic to ensure that my feature contribution does not contain any of the following:
- hardcoded values (the failure message is a named constant, and no coordinates are hardcoded in the service)
- duplicate code (the distance calculation is reused from is_within_radius, not rewritten)
- dead code
- unnecessary function calls
- excessive conditional logic (one condition, two return paths)
- deep nesting
- high cyclomatic complexity
- classes/modules/functions with many unrelated responsibilities

This work is written in location_service.py because it is the existing service that owns location rules, and the target check shares its distance function and result type.
This work belongs in process 4, "Evaluate photo", in the game loop DFD because the photo check now also reads the target's location to decide whether the answer can be correct.

Below are testing receipts.

The functionality works correctly because the happy path tests involving the player at the exact target location and inside the target radius passed.
I wrote tests to cover abnormal situations involving a player outside the radius, a player at (0, 0), and a target with a larger radius admitting a point the smaller one rejects, and they passed.
I checked that these negative cases (outside radius, (0, 0)) failed as expected by [how you checked, e.g. temporarily changing the radius or comparison and watching the tests fail].
Among these tests, none are integration tests; all are unit tests, and integration tests are not required because the function is pure (no database, network or file access), so there is nothing to integrate.
These tests are included in the directory tests/test_target_location_service.py, or tests/backend/ if you moved it.
This new test PR did not break anything else in the system because ran docker compose exec backend pytest, all passing; attach screenshot.  




For PR #155:

As part of requirement "Evaluate image" (with "Location check"), the user needs to start a play, listen to an audio clue, travel to the matching room, take a photo of it and submit the photo along with their device location. Therefore, I implemented code so that the system can decide whether a submission counts as a correct answer: the player must be inside the target's radius AND the photo must contain the expected room code. This supports the student/player user group. No endpoint calls it yet, so nothing is user-visible in this PR.

This PR does not change the database. Photo bytes are the only user-supplied data it validates, and an unreadable image is rejected with a ValueError by the existing decoder in ocr_service, which check_answer lets propagate. 

When I reviewed check_answer and its calls to verify_location_with_target and matches_room for this functionality, I noticed that my first draft imported and called verify_target_location, a function that does not exist in location_service.py (the existing function is verify_location_with_target). That is problematic because the module would fail on import and the feature would never run. Therefore, I changed the import and the call to verify_location_with_target.
When I reviewed the same code, I also checked that matches_room raises ValueError on unreadable images and that check_answer does not swallow it. This is intentional: a bad upload is a client error, not a wrong answer, so the router that calls this will map it to a 4xx rather than a 500..
The PR does not contain any temporary workaround because the target's location and room code are passed in as parameters instead of hardcoded, so the logic is unchanged once a target repository supplies them. (check_answer will later take a target_id and fetch these itself, but that changes the inputs, not the logic.)
The PR only contains small functions that are 6 lines long (check_answer, excluding its docstring).
I read the diff line by line against this checklist and searched the repo for existing answer-checking logic to ensure that my feature contribution does not contain any of the following:
- hardcoded values (the two result messages are named constants; no coordinates or room codes in the service)
- duplicate code (it reuses verify_location_with_target and matches_room instead of reimplementing either)
- dead code
- unnecessary function calls (OCR is not called at all when the location check fails)
- excessive conditional logic (two guard clauses, then success)
- deep nesting
- high cyclomatic complexity
- classes/modules/functions with many unrelated responsibilities (location_service knows nothing about photos, ocr_service knows nothing about GPS, and answer_service is the only place that combines them)

This work is written in the new file services/answer_service.py because the rule "a correct answer needs both a valid location and a matching photo" is business logic that belongs in the Services layer, not the router, and putting it in either existing service would couple location and OCR. The dependency only goes one way (answer_service imports the other two).
This work belongs in process 4, "Evaluate photo", in the game loop DFD because it is the step that decides whether the submitted photo is a correct answer, and it now also reads the target's location.
Below are testing receipts.

The functionality works correctly because the happy path test involving a player at the target with a photo containing the matching room code passed.
I wrote tests to cover abnormal situations involving a player at the target whose photo does not contain the code, a player far from the target whose photo does contain the code, and unreadable image bytes, and they passed.
I checked that these negative cases involving wrong room and wrong place failed as expected I also wrote a test that OCR is never called when the location check fails.
When I reviewed test_ocr_is_skipped_when_location_fails, I noticed that it only proves OCR was skipped if the fake is installed on the name answer_service actually uses, which is a risk because patching the wrong import path would let the test pass for the wrong reason. Therefore, I patched services.answer_service.matches_room (where it is looked up) and asserted on the recorded calls list.
Among these tests, all are unit tests except test_unreadable_image_error_propagates_when_at_target, which runs the real image decoder in ocr_service and is a light integration test. A full integration test is not required yet because there is no endpoint, and OCR is faked everywhere else so the EasyOCR model is never loaded.
These tests are included in the directory tests/backend/test_answer_service.py.
This new test PR did not break anything else in the system because I ran docker compose exec backend pytest with all tests passing.