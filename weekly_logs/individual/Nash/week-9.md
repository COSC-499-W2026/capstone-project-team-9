# Individual Log - Week 9

## **For PR #242: Authentication Setup #242** https://github.com/COSC-499-W2026/capstone-project-team-9/pull/242

### Implementation
As part of the user login and authentication requirements, a registered user needs to be able to securely log in using their email address and password. After successful authentication, the system must generate an access token that identifies the logged-in user. The client must then be able to provide this token when accessing protected API endpoints. The system must validate the token, identify the corresponding user, and reject requests containing missing, invalid, tampered, or expired tokens.

Therefore, I implemented the following functionality:
- Added src/core/security.py to handle password hashing, password verification, access token generation, and access token validation.
- Implemented encrypted JWT access tokens using the jwcrypto library with the A256GCM encryption algorithm.
- Added a 30-minute expiration time for access tokens to limit how long a token remains valid.
- Implemented authentication secret validation using the AUTH_TOKEN_SECRET environment variable. The secret must contain at least 32 characters.
- Added a token-generation function that stores the user's database ID and token expiration timestamp in the encrypted token payload.
- Added a token-validation function that decrypts tokens, validates their headers and payloads, checks expiration, and returns the user's database ID when the token is valid.
- Updated src/core/dependencies.py to configure FastAPI's OAuth2PasswordBearer and introduce get_current_user(), which retrieves the authenticated user from the database using the ID stored in the access token.
- Added CurrentUserDep as a reusable dependency for endpoints that require an authenticated user.
- Updated src/routers/login_router.py with a POST /login/token endpoint that accepts OAuth2 password form credentials, authenticates the user, and returns an encrypted access token.
- Added a GET /login/me endpoint that retrieves the currently authenticated user's information using their bearer token.
- Added a TokenResponse schema in src/schemas/login_schema.py to define the access token response structure.
- Added get_by_id() to src/repositories/user_repo.py to retrieve users using their database IDs.
- Updated src/services/login_service.py to reuse the password-verification functionality from core/security.py.
- Updated src/services/user_service.py to reuse the password-hashing functionality from core/security.py, removing the previous duplicate implementations.
- Added jwcrypto as a project dependency in pyproject.toml.
- Updated .env.example and docker-compose.yaml to configure the authentication secret through environment variables.
- Added tests covering password hashing, password verification, OAuth2 authentication, token generation, token encryption, token expiration, and invalid authentication attempts.

### Verification and problem-solving
When I reviewed core/security.py, I verified that password hashing and verification use bcrypt with randomly generated salts. I also verified that the generated password hashes do not contain the original passwords and that different calls to the hashing function produce different hashes for the same password.

When I reviewed the access token generation functionality, I verified that the token contains the user's database ID and an expiration timestamp. The token is encrypted using the A256GCM algorithm, and its protected header specifies the expected encryption configuration.

When I reviewed decode_access_token(), I verified that it decrypts the token using the configured secret and checks the token's algorithm, encryption method, type, user ID, and expiration timestamp. Invalid or expired tokens return None instead of identifying a user.

When I reviewed the authentication secret validation, I verified that the application rejects missing secrets and secrets shorter than 32 characters. This prevents the authentication system from operating with an inadequately configured secret.

When I reviewed core/dependencies.py, I verified that OAuth2PasswordBearer extracts the bearer token from incoming requests and that get_current_user() uses the decoded database ID to retrieve the corresponding user through get_by_id(). This allows other endpoints to reuse the authenticated-user dependency instead of implementing token validation independently.

When I reviewed login_router.py, I verified that /login/token authenticates users through the existing authenticate_user() service before generating an access token. Incorrect credentials result in HTTP 401 Unauthorized with a WWW-Authenticate: Bearer header.

I also verified that /login/me uses the current-user dependency and returns the authenticated user's information. If the token is missing, invalid, or expired, the endpoint returns HTTP 401 Unauthorized.

Finally, I reviewed the changes to user_service.py and login_service.py. I verified that password hashing and verification are now imported from core/security.py rather than duplicated across multiple services.
Engineering Practices
The PR does not contain any temporary workaround because it establishes a reusable authentication implementation that can be extended as additional protected endpoints are introduced. Token generation, token validation, user retrieval, and HTTP request handling are separated into their respective modules.

The functions are relatively small and focused:
- hash_password() handles password hashing.
- verify_password() handles password verification.
- _token_secret() validates and retrieves the authentication secret.
- _token_key() derives the encryption key from the configured secret.
- create_access_token() generates encrypted access tokens.
- decode_access_token() validates access tokens and retrieves the user ID.
- get_current_user() retrieves the authenticated user from the database.
- issue_access_token() handles OAuth2 login requests and generates access tokens.
- get_logged_in_user() returns information about the authenticated user.

I reviewed the implementation for the following potential issues:
Hardcoded values:
- The authentication secret is retrieved from the AUTH_TOKEN_SECRET environment variable instead of being hardcoded.
- The token expiration duration is defined once using ACCESS_TOKEN_EXPIRE_SECONDS.
- The encryption algorithm and token configuration are explicitly defined because the application must use a consistent encryption format.
Duplicate code:
- Password hashing and verification are centralized in core/security.py.
- The login and registration services reuse the same password-handling functions.
Dead code:
- The new functions are used by the authentication endpoints and dependencies.
- The existing password-hashing implementations in user_service.py were removed after being centralized.
Unnecessary function calls:
- Token validation stops when decryption or payload validation fails.
- User retrieval only occurs when a valid user ID is obtained from the token.
Excessive conditional logic:
- The token-validation function uses straightforward checks for invalid headers, user IDs, and expiration timestamps.
- The authentication endpoints use simple checks to handle unsuccessful authentication.
Deep nesting:
- The token-validation function uses early returns and exception handling rather than deeply nested conditions.

Unrelated responsibilities:
- Password management and token operations are handled in core/security.py.
- Current-user retrieval is handled through core/dependencies.py.
- Database user retrieval is handled in user_repo.py.
- OAuth2 request and response handling is handled in login_router.py.

### Architecture impacts
This work is written in the following files because each belongs to a distinct layer of the existing FastAPI backend:
- src/core/security.py contains the password hashing, password verification, encrypted token generation, and token validation functionality.
- src/core/dependencies.py defines reusable authentication dependencies and retrieves the currently authenticated user.
- src/repositories/user_repo.py provides database access for retrieving users by their IDs.
- src/services/login_service.py handles user credential authentication.
- src/routers/login_router.py exposes the OAuth2 token endpoint and authenticated-user endpoint.
- src/schemas/login_schema.py defines the structure of token responses.
- src/services/user_service.py reuses the centralized password-hashing functionality.
- pyproject.toml, .env.example, and docker-compose.yaml configure the new dependency and authentication secret.
This work belongs in the application's user authentication process in the DFD because it establishes how users authenticate and how the system identifies authenticated users when they access protected endpoints.

The authentication data flow is:
1. The client submits an email address and password to POST /login/token using OAuth2 password form data.
2. The login router passes the credentials to authenticate_user().
3. The login service retrieves the user from the database and verifies the supplied password using bcrypt.
4. If authentication succeeds, the router calls create_access_token() to generate an encrypted JWT containing the user's database ID and expiration timestamp.
5. The client receives the access token and stores it for subsequent authenticated requests.
6. When the client accesses a protected endpoint, it provides the token through the HTTP Authorization header using the Bearer scheme.
7. OAuth2PasswordBearer extracts the token, and get_current_user() calls decode_access_token() to validate it.
8. If the token is valid, the system retrieves the corresponding user from the database using get_by_id().
9. If the token is invalid, missing, or expired, the system rejects the request with HTTP 401 Unauthorized.
This PR establishes authentication and user identification, but it does not yet implement role-based authorization. All authenticated users are currently treated the same, regardless of whether they are students, instructors, or administrators. Restricting endpoints based on user roles is handled separately.

### Testing Receipts
The functionality is covered by the following happy-path tests:
- test_hash_password verifies that passwords are hashed rather than stored as plain text and that the resulting hash can be verified.
- test_hash_password_uses_different_salts verifies that hashing the same password multiple times produces different hashes while both remain valid.
- test_verify_password_rejects_wrong_password verifies that password verification rejects an incorrect password.
- test_oauth2_token_authenticates_user verifies that a user can successfully authenticate through the OAuth2 token endpoint, receive an access token, and retrieve their information through /login/me.
- test_access_token_is_encrypted_jwt verifies that the generated token uses the expected encryption configuration and contains the correct user ID and expiration timestamp.
The tests also cover abnormal authentication outcomes:
- test_oauth2_token_rejects_invalid_password verifies that an incorrect password results in HTTP 401 Unauthorized.
- test_me_rejects_tampered_token verifies that modifying an encrypted token causes authentication to fail.
- test_me_rejects_expired_token verifies that an expired access token is rejected.
- test_me_rejects_missing_or_invalid_token verifies that requests without an authentication token or with an invalid token are rejected.
I also included negative tests for authentication secret configuration:
- test_token_operations_require_long_authentication_secret verifies that token generation and validation reject missing or insufficiently long authentication secrets.

The tests use a test authentication secret configured through monkeypatch rather than relying on the actual development environment secret. This allows the tests to verify authentication behavior without modifying the project's environment configuration.

Among these tests, the password hashing tests in test_security.py are unit tests of the security functionality. The token generation and validation checks also test individual security functions. The OAuth2 endpoint tests in test_login_router.py exercise the authentication process through FastAPI's TestClient, providing integration-level coverage of the token endpoint, bearer authentication, database user retrieval, and HTTP responses.

The tests are included in:
- tests/backend/test_core/test_security.py
- tests/backend/test_repos/test_user_repo.py
- tests/backend/test_routers/test_login_router.py
- tests/backend/test_services/test_login_service.py
- tests/backend/test_services/test_user_service.py
This PR does not break anything else in the system because the existing password-hashing functionality was retained and centralized rather than replaced with a different password format. 

This was a large PR, larger than we are meant to commit, but in researching and implementing authentication, there were multiple fixes that had to happen before the PR was merged, and therefore ended up having lots of small changes, in lots of files.


## For PR #250: User Roles #250

### Implementation
As part of the user authentication requirements, the system needs to distinguish between different types of users so that it can support students, instructors, and administrators. When a user registers, the system must automatically assign them the default student role rather than allowing them to select their own permissions. The system must also store and return role information consistently throughout the user management and authentication processes.

Additionally, users should be able to share the same name because names are not necessarily unique identifiers. Email addresses, however, must remain unique so that each account can be identified independently.

Therefore, I implemented the following functionality:
- Added a UserRole enum to src/models/user_model.py with three supported roles: student, instructor, and admin.
- Added a role field to the User model, with a default value of student.
- Added a database-level CheckConstraint named ck_user_role to restrict stored role values to student, instructor, or admin.
- Updated the User model to remove the uniqueness restriction on the name field while retaining the unique constraint on email addresses.
- Updated src/repositories/user_repo.py so that create_user() accepts an optional role argument, defaulting to UserRole.STUDENT.
- Updated the repository to convert supplied role values into the UserRole enum before creating a user.
- Updated src/services/user_service.py so that registration explicitly assigns UserRole.STUDENT to newly registered users.
- Removed the username uniqueness check from register_user(), allowing multiple users to register with the same name.
- Updated src/schemas/user_schema.py so that UserResponse includes the user's role.
- Updated src/routers/login_router.py to include role information in the response from /login/me.
- Updated src/routers/user_router.py to include role information in individual user responses and user lists.
- Updated repository, service, registration, and login tests to verify the new role functionality and the removal of username uniqueness restrictions.

### Verification and problem-solving
When I reviewed user_model.py, I verified that the UserRole enum defines the three supported roles and that the role field defaults to student. I also reviewed the database check constraint to verify that invalid role values cannot be stored through normal database operations.

When I reviewed the User model's name and email fields, I verified that the name field no longer has a uniqueness constraint while the email field retains its unique constraint. This allows multiple accounts to share the same name without allowing duplicate email addresses.

When I reviewed user_repo.py, I verified that create_user() accepts a role argument and defaults to the student role when no role is provided. I also verified that the repository converts the supplied role into a UserRole value before creating the database record.

When I reviewed user_service.py, I verified that register_user() no longer checks whether a username already exists. Instead, it normalizes the email address, checks whether the email is already registered, hashes the password, and creates the user with the student role.

When I reviewed user_schema.py and the registration functionality, I verified that role assignment is controlled by the backend rather than accepted from the client.

When I reviewed user_router.py and login_router.py, I verified that role information is included in the UserResponse returned by the relevant endpoints. This allows the frontend to identify the user's assigned role after registration, login, or retrieval of authenticated-user information.

Finally, I reviewed the updated tests to verify that they cover duplicate names, duplicate email addresses, default role assignment, email normalization, and role information in API responses.
Engineering Practices
The PR does not contain any temporary workaround because role management is implemented directly within the existing user model, repository, service, and schema structure. The implementation extends the existing user management functionality rather than introducing a separate role-management system.

The functions are relatively small and focused:
- create_user() handles database user creation, including role assignment.
- register_user() handles registration validation, email normalization, password hashing, and default role assignment.
- The user router functions handle returning user information, including role data.
- The login router's /me endpoint returns the authenticated user's information, including their role.

I reviewed the implementation for the following potential issues:
Hardcoded values:
- Supported role values are defined centrally in the UserRole enum.
- The default student role is defined in the model and explicitly assigned during registration.
- The database check constraint uses the same three supported role values to prevent invalid roles from being stored.
Duplicate code:
- Role values are centralized in UserRole rather than independently defined throughout the application.
- Existing user creation and registration functionality is reused instead of introducing additional user-management implementations.
Dead code:
- The removed username uniqueness checks are no longer part of the registration process.
- The new role functionality is used by the user model, repository, services, schemas, and API responses.
Unnecessary function calls:
- Registration only checks for an existing email address because duplicate names are now permitted.
- User creation directly assigns the role rather than requiring an additional role-management operation.
Excessive conditional logic:
- The registration service no longer needs a conditional check for duplicate usernames.
- Role validation is handled through the enum and database constraint rather than additional conditional statements.
Deep nesting:
- The updated registration and repository functionality does not introduce additional nested conditional structures.
High cyclomatic complexity:
- The changes mainly extend existing functions with role assignment and response fields.
- The removal of username uniqueness checks also reduces the number of decision points in the registration service.

Unrelated responsibilities:
- Role definitions and database constraints are contained in the User model.
- User creation is handled by the repository.
- Default role assignment is handled by the registration service.
- Role response formatting is handled by the schemas and routers.

### Architecture impacts
This work is written in the following files because each belongs to a distinct layer of the existing FastAPI backend:
- src/models/user_model.py defines the supported user roles and stores each user's assigned role.
- src/repositories/user_repo.py handles database operations for creating users with their assigned roles.
- src/services/user_service.py controls the default role assignment during registration.
- src/schemas/user_schema.py defines the user response structure, including role information.
- src/routers/user_router.py returns role information through the user management endpoints.
- src/routers/login_router.py returns role information for authenticated users.
This work belongs in the user management and authentication data flow in the DFD because user roles are now part of the information stored and retrieved throughout the application's user management process.

The user registration and retrieval data flow is:
1. A client submits a registration request containing a name, email address, and password.
2. The registration schema validates the submitted information.
3. The registration service normalizes the email address and checks whether it is already registered.
4. The service hashes the password and assigns the default student role.
5. The repository creates the user record with the assigned role.
6. The database stores the user's information and enforces the valid role constraint.
7. When the client requests user information, the user router retrieves the corresponding records and includes each user's role in the response.
8. When an authenticated user accesses /login/me, the login router returns their name, email address, and role.
This PR establishes the data structure and default assignment for the three user roles. However, it does not yet implement role-based authorization or restrict access to endpoints based on whether a user is a student, instructor, or administrator. That functionality will need to be implemented separately.

### Testing Receipts
The functionality is covered by the following happy-path tests:
- The updated user repository creation tests verify that users can be created successfully with the expected information.
- test_create_user_allows_duplicate_names verifies that multiple users can be created with the same name when they have different email addresses.
- The updated user service registration tests verify that newly registered users receive the default student role.
- test_register_user_normalizes_email verifies that email addresses are converted to lowercase during registration.
- test_register_user_allows_duplicate_name verifies that registration succeeds when another user already has the same name.
- test_register_uses_student_role_and_ignores_submitted_role verifies that users receive the student role even if they submit a different role, such as admin, in their registration request.
- The updated login router tests verify that authenticated-user responses include the user's role.
- The updated user router tests verify that user responses and user lists include role information.
The tests also cover abnormal situations:
- The updated repository tests verify that creating two users with the same email address raises DuplicateUserError.
- The updated service tests verify that duplicate email addresses are rejected during registration.
- The database constraint is tested to verify that invalid role values cannot be stored.
I also included negative tests for registration and role validation:
- The registration test verifies that a submitted admin role is ignored and the backend assigns the student role instead.
- The database constraint test verifies that unsupported role values are rejected.
- The duplicate email tests verify that email uniqueness is maintained even though duplicate names are now permitted.
Among these tests, the repository tests in test_user_repo.py are unit-level tests of the database access functionality using a test database session. The service tests in test_user_service.py test the registration logic and role assignment. The router tests in test_user_router.py and test_login_router.py exercise the API endpoints through FastAPI's TestClient, providing integration-level coverage of request handling and response formatting.

The tests are included in:
- tests/backend/test_repos/test_user_repo.py
- tests/backend/test_services/test_user_service.py
- tests/backend/test_routers/test_user_router.py
- tests/backend/test_routers/test_login_router.py
This PR does not break anything else in the system because the existing user registration and login functionality has been updated to include role information while retaining the existing authentication and user retrieval processes. 

## To Note
Currently none of our tests are passing in Github, this is because of a CI issue that we have emialed Dr. Hui about, and are fixing. We are, however, testing every branch full on our own computers when we review them.
This means that I cannot provide Github testing recipes this week, but both of my PR's have been checked at least three time, and we have decided to merge all PR's this week anyways after being reviewed fully.