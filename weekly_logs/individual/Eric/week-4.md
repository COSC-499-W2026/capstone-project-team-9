For PR #23:

 As part of requirement basic pytest setup, the user needs to install dependencies from requirements.txt, personal tests and run pytest, and have github automatically run tests when a PR is created.

 Therefore, I implemented code so that developers on the team can run a pytest with shared fixtures and mocks,  and automatic test runs on GitHub.

 When I reviewed pytest.ini, tests/conftest.py, tests/test_tests.py, and .github/workflows/tests.yml for this functionality, I did not find any problems with it because I ran pytest locally in a virtual environment after installing from requirements.txt, and all tests passed with "configfile: pytest.ini" shown in the output, along with that when i created the PR git automatically ran the tests.

 The PR does not contain any temporary workaround because the pytest configuration and workflow are the long-term setup. The only placeholders are the sample_data and mock_api_client fixtures and test_tests.py, which are scaffolding to be replaced by real tests.

 The PR only contains small functions that are under 10 lines long.

 I did read through each file, confirm every fixture is used by a test, and confirm nothing is repeated across files to ensure that my feature contribution does not contain any of the following:
 - hardcoded values
 - duplicate code
 - dead code
 - unnecessary function calls
 - excessive conditional logic
 - deep nesting
 - high cyclomatic complexity
 - classes/modules/functions with many unrelated responsibilities

 This work is written in pytest.ini, tests/conftest.py, tests/test_tests.py, and .github/workflows/tests.yml because pytest reads its config from the repo root, automatically loads shared fixtures from conftest.py in the tests folder, and GitHub only runs workflows located in .github/workflows.

 This work belongs in no DFD process because this PR adds test infrastructure and does not contain application logic.

Test receipts for PR #23:

this pr was the initial setup for testing, the only test i had in place was a simple placeholder assert, which worked as intended.