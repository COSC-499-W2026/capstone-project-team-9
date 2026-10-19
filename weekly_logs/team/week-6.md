# Week 6 Team Log

## Focus

This week, we focused on core game-loop infrastructure:

- User registration
- The PostgreSQL database
- The first frontend-backend connection: Play button to location verification
- The OCR portion of the photo check

This work covered the Sign-up requirement in `docs/proposal/new-reqs-and-timeline.md`, the “Location check” and “Evaluate image” requirements, issue #8, and the team contract’s testing practices. Our goal was to deliver a working database, a validated registration endpoint, a usable Play/location check, and a working room-code reader.

## Work completed

- **Nash — User registration (PR #121):** Built schema validation for name, email, and password; a service with duplicate checking, salted password hashing, and ID assignment; a `POST /users/register` endpoint (201 on success, 409 on duplicate); and tests.
- **Joe — Frontend and location verification (PRs #113 and #125):** Built a Vue 3 + Vite Play button that calls `POST /location/verify`, creating our first frontend-backend connection. Set up frontend testing with Vitest and added CI.
- **Ian — PostgreSQL setup (PR #122):** Added PostgreSQL as a Docker service, along with `.env.example` and README documentation, closing issue #8.
- **Eric — OCR and CI coverage (PRs #120 and #124):** Built the EasyOCR room-code service, which handles the text-recognition portion of the photo check. The endpoint is not yet connected because the scene-checker portion is being handled separately. Also added coverage reporting to CI.

## Team approach

We considered splitting work by layer, with one person handling the backend and another handling the frontend. Instead, we chose vertical slices so each person could own a feature end-to-end, including its tests.

## Progress against our goal

We met this week’s goal based on merged PRs and successful test runs:

- PRs #113, #122, #120, and #125 are merged.
- The backend suite and all frontend tests pass.
- The location flow was verified end-to-end in Brave using spoofed GPS: on-campus users were allowed, and off-campus users were blocked.

PRs #121 and #124 are complete and open for review. Next week, we plan to merge them and connect the OCR endpoint once the scene-checker portion is ready.

## Reviews and maintainability

To avoid duplicated logic, tangled dependencies, and ripple-effect changes, we reviewed every PR and checked new code against the DFDs and system architecture.

- **Joe’s review:** Confirmed there are no hardcoded values (the API base path is a named constant), functions are 1–12 lines, and frontend files mirror the backend’s layering with one API file per router. CI uses `npm ci` with a committed lockfile.
- **Eric’s review:** Confirmed the OCR service uses named constants and 2–10 line functions, and that third-party library calls stay in the Services layer as specified by our architecture.
- **Nash’s work:** Followed the established router/service/schema layering. The branch history shows that a temporary database interaction was added and then reverted during review.
- **Ian’s PR:** Documented the manual verification steps for database setup.

## Issues found and resolved

Review and testing caught several problems, all of which were fixed:

- Joe found that the new Vitest dependencies were missing from the running container. We fixed this by restarting with `docker compose up`.
- Eric found a mismatch in the OCR character-translation table, where commonly confused letters were mapped to the wrong digits. We corrected the mappings and added parametrized tests.
- A stale container was missing `cv2`. We rebuilt it, switched to CPU-only Torch, and baked the OCR model weights into the image.
- We removed a dead code branch.
- A test was silently skipped because of an incorrect file path. We corrected the path and reran the tests with `-rs` to confirm that nothing was skipped.

## Maintainability check

The team reviewed the codebase for the following issues and found no indications of them:

- Similar logic implemented multiple times
- Excessive dependencies between modules
- Changes in one component requiring changes elsewhere
