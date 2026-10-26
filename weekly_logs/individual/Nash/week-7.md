## **For PR #140** https://github.com/COSC-499-W2026/capstone-project-team-9/pull/140

As part of the user registration requirement, users need to create accounts without manually assigning database identifiers.

Therefore, I refactored the code from PR #121 https://github.com/COSC-499-W2026/capstone-project-team-9/pull/121 by removing manual ID assignment from the user service and removing the `id` field from the `UserResponse` schema. I also simplified the registration endpoint to delegate account creation to the service.

When I reviewed the router, schema, and service changes, I verified that the code no longer relies on manually assigned user IDs or an ID field in registration responses.

This work belongs in `src/routers/user_router.py`, `src/schemas/user_schema.py`, and `src/services/user_service.py` because these files handle registration requests, response structures, and user registration logic, respectively.

### Testing Receipts

The functionality should be tested by verifying that user registration succeeds and returns the expected username and email without an ID field.

Negative tests should verify that invalid registration data is rejected and that removing manual ID assignment does not break existing registration functionality.

The relevant tests belonged in the project's user_test file, but has since been changed.



## **For PR #152** https://github.com/COSC-499-W2026/capstone-project-team-9/pull/152

As part of the user registration requirement, users need to be able to register an account by providing a username, email address, and password. The system must validate the submitted information, prevent duplicate usernames and email addresses, securely hash passwords before storing them, and allow existing user records to be retrieved from the database.


**Implementation**

Therefore, I implemented code so that users can register accounts using the FastAPI backend, retrieve registered users, and receive appropriate responses when registration fails. The repository uses SQLModel and database sessions to create and retrieve user records from PostgreSQL. The service validates uniqueness, normalizes email addresses to lowercase, and hashes passwords before saving them. The router returns HTTP 201 when registration succeeds, HTTP 409 when a username or email already exists, and HTTP 422 when submitted data fails validation.
When I reviewed the user_model.py file, I verified that the User model defines an integer primary key, a username with length constraints and a uniqueness constraint, an email address with a uniqueness constraint, and a field for storing the hashed password. These constraints help maintain data integrity and prevent duplicate user records.

When I reviewed the user_repo.py file, I verified that the repository uses SQLModel queries and database sessions rather than temporary in-memory storage. The create_user function commits new records and refreshes the user object after a successful commit. It also catches database IntegrityError exceptions, rolls back failed transactions, and raises DuplicateUserError when a database uniqueness constraint is violated.

When I reviewed the user_router.py file, I verified that the registration endpoint delegates account creation to the service and translates duplicate-user errors into HTTP 409 responses. The user-listing endpoint retrieves records from the database and returns only the username and email address.

When I reviewed the user_service.py file, I verified that registration checks whether the username or email already exists before creating an account. Email addresses are converted to lowercase to ensure consistent storage, and passwords are hashed before being passed to the repository.

When I reviewed the test_user_repo.py, test_user_router.py, and test_user_service.py files, I verified that the tests cover repository operations, registration validation, duplicate-user handling, password hashing, and email normalization. The tests use a database session fixture for repository and router tests and mocked dependencies for isolated service tests.


**Temporary workarounds and design considerations**

The PR does not contain a temporary in-memory user repository or hardcoded user storage as a substitute for the database. User records are created and retrieved through SQLModel database sessions, providing a maintainable approach that can be used as the application grows. The tests use sample user data to verify functionality, but this data is test input rather than a replacement for persistent storage.


**Function size and code quality**

I reviewed the user model, repository, service, router, and test files to identify unnecessary complexity and maintainability issues. I separated database operations into the repository, registration logic into the service, HTTP request handling into the router, and persistence constraints into the model.

The repository functions reuse the same SQLModel User model and database session instead of duplicating database access logic. The service performs email normalization in one place, and password hashing is handled by a dedicated function. The router delegates registration and retrieval operations to existing functions rather than implementing database queries directly.

I also reviewed the code for hardcoded application data, duplicate code, dead code, unnecessary function calls, excessive conditional logic, deep nesting, high cyclomatic complexity, and unrelated responsibilities.


## **Testing**

I wrote tests to cover abnormal situations involving duplicate usernames, duplicate email addresses, invalid email formats, passwords that are too short, and missing required registration fields. The repository tests expect DuplicateUserError when a duplicate username or email is submitted. The service tests verify that duplicate registrations raise the appropriate exception and that the repository's create_user function is not called for a duplicate username or email.
I checked negative cases involving invalid email addresses, short passwords, missing usernames, duplicate usernames, and duplicate email addresses. The router tests expect HTTP 422 for invalid registration data, while the service and repository tests expect DuplicateUserError for duplicate accounts. These tests are designed to fail if the system accepts invalid input or allows duplicate records.
When I reviewed test_hash_password and test_hash_password_uses_different_salts, I noticed that the original assertions expected a custom password-hashing format containing a salt and a hexadecimal hash separated by a colon. These assertions are implementation-specific and would not be appropriate if the password-hashing implementation changed to bcrypt. Therefore, the tests must be updated to verify the actual password-hashing implementation, such as checking that the stored hash differs from the original password and that the hashing library can verify the password against the resulting hash.
Among these tests, the repository tests are database integration tests because they execute database operations through a SQLModel session. The router tests are API integration tests because they send HTTP requests through FastAPI's TestClient and verify responses while overriding the database session dependency. The service tests are unit tests because they isolate registration logic by replacing repository functions with mocked or substituted implementations.
These tests are included in the following directories:
- tests/backend/test_user_repo.py
- tests/backend/test_user_router.py
- tests/backend/test_user_service.py

The test PR is intended to avoid breaking existing functionality because the tests focus on the user model, repository, service, and router without intentionally changing unrelated application behavior. The existing location tests should also be run as regression tests to check that the user registration changes do not affect the location feature.

After running the full test suite successfully, I can confirm that the new user tests do not break existing functionality and attach the test output as evidence.



## **For PR #157** https://github.com/COSC-499-W2026/capstone-project-team-9/pull/157

As part of the user registration requirement, users need to create accounts without exposing their passwords if the database is compromised.

Therefore, I updated `user_service.py` to use bcrypt for password hashing and verification, configured bcrypt with 12 rounds, and added bcrypt as a project dependency in `pyproject.toml`. I also updated the service tests to verify password hashes and unique salts.

When I reviewed the password hashing implementation, I verified that passwords are encoded using UTF-8, hashed with bcrypt, and stored as strings. The verification function uses bcrypt to check a password against its stored hash.


**Temporary workarounds and design considerations**

The PR does not contain a temporary workaround because it uses a dedicated password-hashing library designed for securely storing passwords.

The PR contains small, focused functions: `hash_password()` and `verify_password()`, each approximately 5 lines long, excluding blank lines.

I reviewed the changes to ensure password hashing and verification have separate responsibilities, bcrypt is configured consistently, and the tests verify successful password verification and different hashes for the same password. The implementation avoids storing plaintext passwords.

This work belongs in `app/backend/src/services/user_service.py` because password hashing and verification are part of the user service's business logic. The bcrypt dependency belongs in `app/backend/pyproject.toml`, and the associated tests belong in `tests/backend/test_user_service.py`.

This work belongs in the user registration and authentication processes in the DFD because passwords must be hashed before storage and verified when a user attempts to authenticate.


## **Testing**

The functionality works correctly because the tests verify that bcrypt hashes passwords successfully and that the original password can be verified against the stored hash.

I wrote tests to cover abnormal situations involving repeated password hashing. The tests verify that hashing the same password produces different hashes due to unique salts, while both hashes remain valid for password verification.

These tests are included in the directory `tests/backend/test_user_service.py`.
