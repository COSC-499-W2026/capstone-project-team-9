**For PR #39**

To improve the project's dependency management and test configuration, the user needs to be able to install the project dependencies consistently and run the automated test suite using the project's standard Python packaging configuration.

Therefore, I implemented and updated the project configuration so that:
- The project dependencies are defined in pyproject.toml.
- Test dependencies (pytest, pytest-cov, and pytest-mock) are defined as optional test dependencies.
- Pytest is configured to discover tests from the tests directory and use src as the Python path.
- The test workflow installs the project and its test dependencies before running the test suite.
-  The previous requirements.txt and pytest.ini configuration files are removed because their configuration is now consolidated in pyproject.toml.

When I reviewed the changes to .github/workflows/tests.yml, pyproject.toml, pytest.ini, and requirements.txt, I did not find any problems with them because the dependency installation and test configuration are consolidated into the standard Python project configuration, and the CI workflow continues to execute the test suite with coverage reporting.