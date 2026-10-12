**For PR #39**

To improve the project's dependency management and test configuration, the user needs to be able to install the project dependencies consistently and run the automated test suite using the project's standard Python packaging configuration.

Therefore, I implemented and updated the project configuration so that:
- The project dependencies are defined in pyproject.toml.
[build-system]
- requires: Specifies that setuptools version 61 or higher is needed to build the project
- build-backend: Tells Python tools to use setuptools to build thepackage
[project]
- Holds the name, version, and dependency list for the project
[project.optional-dependencies]
- pytest: Runs the tests
- pytest-cov: Measures how much of the code is covered by tests
- pytest-mock: Provides tools for mocking objects and functions during tests
[tool.pytest.ini_options] For test configuration
- testpaths = ["tests"]: Tells pytest to look for tests in the tests/ directory by default
- pythonpath = ["src"]: Adds the src/ directory to Python's import path, making modules stored there easier to import in tests
- addopts = "-v": Enables more detailed output about each test

- *.egg-info was also added to .gitignore so that the automatically created documentation is ignored

How to test
- Run in terminal: pip install -e ".[test]"
- Run in terminal: pip list
- Check if dependencies are installed: fastapi, pytest, pytest-cov, and pytest-mock
- Run in terminal: pip install build
- Then: python -m build
- Run: pytest
- The previous requirements.txt and pytest.ini configuration files are removed because their configuration is now consolidated in pyproject.toml.

When I reviewed the changes to .github/workflows/tests.yml, pyproject.toml, pytest.ini, and requirements.txt, I did not find any problems with them because the dependency installation and test configuration are consolidated into the standard Python project configuration, and the CI workflow continues to execute the test suite with coverage reporting.

**Admin tasks
I also worked on reworking, fixing, and splitting up our tasks in our project plan. Ian and I worked through our user and functional requirments together. The new document will be linked in our readme.