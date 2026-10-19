For PR #124:

 As part of requirement "Evaluate image" (reading the room number on the door plaque), the user needs to hear the audio clue for a room, find that room, take an in-app camera photo of the door plaque, and submit it so the system can check that the room number in the photo matches the expected room.

 Therefore, I implemented `src/services/ocr_service.py` so that players get a right/wrong answer for the text half of the photo check. It reads room codes (like COM301 or EME0050) from a photo using EasyOCR and reports whether the expected room code is present. The scene checker (comparing against the reference photo) is intentionally a separate PR, so this PR has no endpoint yet; the endpoint needs both verdicts.

 When I reviewed the unit tests for this functionality, I noticed `test_extract_codes_finds_and_corrects[LIB3I4]` returned `LIB304` instead of `LIB314`. This was problematic because the `TO_DIGIT` translation table had mismatched source and target strings, so confusable letters mapped to the wrong digits (for example I became 0 and S became 2), which would have silently broken real plaque reads. Therefore, I realigned the table and added a parametrized test covering S, Z, B and G.

 When I ran the tests the first time, I got `ModuleNotFoundError: No module named 'cv2'`. This was because the container image had been built before I added `easyocr`, `opencv-python-headless` and `numpy` to `pyproject.toml`. Therefore, I rebuilt with `docker compose up --build`. I also updated the `Dockerfile` to install CPU-only torch (so EasyOCR doesn't pull the multi-GB CUDA build) and to bake the EasyOCR model weights into the image so nothing downloads at runtime or in CI.

 When I ran the real-photo test on the LIB314 submission, it failed. The file was only 225x390 pixels, so the plaque text was roughly 8 px tall, which is too small to read reliably. Therefore, I first tried upscaling small images before OCR, but this made the checks much slower and the photo still failed. I reverted to only shrinking large images, kept a third "far" pass for plaques that are small in a large frame, and removed that photo from the test set because it is not representative of what the in-app camera will send.

 The PR does not contain any temporary workaround in the logic. The only temporary element is the test data: the real-photo tests read preset images from `db/submissions`, which stand in for live captures until the app takes real ones (which will not be saved).

 The PR only contains small functions that are [2 to 10] lines long. The longest is `_extract_codes`.

 By re-reading the file and searching for repeated values and unused code, I found that my feature contribution contained dead code: after capping the upscale at 1, the enlarge branch in `_resize_to` could never run. Therefore, I removed the `MAX_UPSCALE` constant and the branch. Now, I can confirm that my feature contribution does not contain any of the following:
 - hardcoded values: contains image sizes, OCR options, the allowed character set and room-code pattern are named constants
 - duplicate code
 - dead code
 - unnecessary function calls
 - excessive conditional logic
 - deep nesting
 - high cyclomatic complexity
 - classes/modules/functions with many unrelated responsibilities

 This work is written in the new file `src/services/ocr_service.py` because the architecture puts core business logic in Services, and Services are what call third-party libraries (here EasyOCR and OpenCV). There is no router or repository yet because the OCR is image-in, text-out and touches no database.

 This work belongs in process "4 Evaluate photo" in the game loop DFD because it checks the player's photo against the expected target and returns match or no match.

Testing receipts for PR #124:

 The functionality works correctly because the happy path tests `test_matches_room_true_when_code_present`, `test_extract_codes_finds_and_corrects` and `test_real_submission_matches_its_own_room` passed. All remaining real submission photos pass; LIB314 was the only one that failed, and it was removed.

 I wrote tests to cover abnormal situations involving no code in the text (`test_extract_codes_ignores_non_codes`), unreadable image bytes (`test_unreadable_bytes_raise_value_error`) and OCR confusions between letters and digits (`test_digit_confusions_map_to_the_right_digit`), and they passed.

 I checked that these negative cases involving a photo of a different room (`test_matches_room_false_for_wrong_room`) were rejected as expected.

 When I reviewed the first version of `test_real_submission_matches_its_own_room`, I noticed it was silently skipped because its path pointed at `tests/db/submissions` instead of the repo-root `db/submissions`, so it passed the run without ever exercising the OCR. Therefore, I fixed the path and ran with `-rs` to confirm nothing was being skipped.

 Among these tests, the extraction, matching, multi-pass and bad-input tests are unit tests (EasyOCR is faked) and `test_real_submission_matches_its_own_room` is an integration test (it runs the real model on real photos).

 These tests are included in the directory `tests/test_ocr_service.py`.
 This new test PR did not break anything else in the system because I ran the full suite with `docker compose exec backend pytest` and all tests passed.




For PR #120:

As part of requirement Coverage reporting, the developer needs to run the test suite, see how much of the code in src/ is covered by tests, and have this reported automatically when a PR is opened. Therefore, I implemented configuration so that all developers on the team can generate coverage reports locally and in CI. It adds a cov.yaml workflow and updates .gitignore, pyproject.toml and the Dockerfile to support it.

When I reviewed cov.yaml, .gitignore, pyproject.toml and the Dockerfile for this functionality, I did not find any problems with it.

The PR does not contain any temporary workaround because it only contains long-term configuration for coverage reporting and no application logic.

The PR contains no functions. It has configuration files only.

This work is written in .github/workflows/cov.yaml, .gitignore, pyproject.toml and the Dockerfile because GitHub only runs workflows located in .github/workflows, coverage dependencies and settings belong in the project’s standard packaging config, the Docker image must contain whatever the container needs to produce reports, and generated coverage files should stay out of version control.

This work belongs in no DFD process because this PR is test and CI infrastructure and does not contain application logic.

Test receipts: no new tests were written in this PR because it only adds coverage reporting for the existing tests.