## **For PR #121**

As part of the user registration requirement, the user needs to perform the following sequence of actions in the system:
1. Submit a registration request containing a name, email address, and password
2. Have the system validate the submitted information, including the name length, email format, and minimum password length
3. Have the system check whether the name or email address has already been registered
4. Receive a successful registration response containing the user's ID, name, and email address if the information is valid and unique
5. Receive an appropriate error response if the submitted information is invalid or the name or email address is already registered


**Implementation**

Therefore, I implemented code so that users can register through the FastAPI endpoint POST /users/register. The functionality validates registration input, detects duplicate names and email addresses, assigns a unique ID, hashes the submitted password, and returns a response that excludes the password and password hash. For this development version, registered users are stored in an in-memory Python list instead of a database.


**Temporary workarounds and design considerations**

The implementation uses in-memory storage as a temporary development approach because a database connection is not required or available for the current testing stage. This approach is intentionally limited: user records are lost when the application restarts, and the data is not shared between separate application workers. The in-memory storage will be replaced with persistent database operations.


**Function size and code quality**

I reviewed the implementation for hardcoded values, duplicate code, dead code, unnecessary function calls, excessive conditional logic, deep nesting, high cyclomatic complexity, and functions with unrelated responsibilities. The current implementation keeps the registration flow relatively simple. However, the in-memory storage and password policy are intentional development choices that should be reviewed later.

## **Testing**
The functionality works correctly for the tested happy paths because the successful user registration test, test_register_user, passed. The test confirmed that a user can register successfully and that the response contains the expected user ID, name, and email address without exposing the password or password hash.
I wrote tests to cover abnormal situations involving duplicate email addresses, duplicate names, invalid email addresses, and passwords shorter than the required minimum. The duplicate-email, duplicate-name, and invalid-email tests passed.
I checked the negative cases involving duplicate registration and invalid email input. The duplicate-registration tests returned HTTP 409 Conflict, and the invalid-email test returned HTTP 422 Unprocessable Entity, as expected.

These tests are included in tests/test_users.py.