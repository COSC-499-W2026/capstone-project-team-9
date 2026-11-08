# ENJIneers Language Game Project

This repo contains the source code for Team 9's Capstone Software Engineering project.

## Links 

### Early Planning

- [🔗 Team Contract](./docs/contract/team-contract.md)
- [🔗 Project Proposal](./docs/proposal/project-proposal.pdf)
- [🔗 Requirements Planning pt.2](https://docs.google.com/document/d/1ib5CDUCnfNi2iX7NgINAJ9l41g_lQKTaRL1nvg-tNc4/edit?usp=sharing)

### System Design

- [🔗 System Architecture](./docs/system-design/system-architecture/system-architecture.md)
- [🔗 Data Flow Diagrams (level 0 and level 1)](./docs/system-design/data-flow-diagrams)
- [🔗 Database Design Documents](./docs/system-design/db-design)

---

## Instructions for Local Development

- [Prerequisites](#prerequisites)
- [Run the app](#run-the-app)
- [Run unit tests](#run-unit-tests)
- [Initialize, seed and inspect the database](#initialize-seed-and-inspect-the-database)
- [Make your IDE happy with a venv](#make-your-ide-happy-with-a-venv)
- [Poke around (Advanced Commands)](#poke-around-advanced-commands)

---

### Prerequisites

#### 🐋 **Docker**

> [!IMPORTANT]
> Our app and tests must be run inside a **Docker container** to ensure that our environments and dependency versions are identical at all times. Our CI runs the test suite in a container built from the same image.
>
> _**You will need Docker Desktop to be [installed](https://docs.docker.com/get-started/get-docker/) and running.**_

#### 🤖 **Just**

> [!IMPORTANT]
> 
> We use [just](https://just.systems) to alias our most terminal common commands, so you don't have to remember long `docker compose` invocations. Run `just` with no arguments at any time to see every available command, grouped by category.
> 
> The commands are defined in the [justfile](./justfile), so go there if you want to see exactly what each one runs!


To [install just](https://just.systems/man/en/installation.html) on your machine, run:
```
# On Mac 
brew install just
``` 
```
# On Windows (Powershell)
winget install Casey.Just
```

#### >_ Terminal Tips

`just` helps you waste less time in the terminal, and so do the following tricks!

> [!TIP]
> 
> - use the `↑` up arrow key to cycle through previous commands
> - use the `tab` key to cycle through files and directories
> - in VS Code, use ``ctrl + ` `` to open and close the built-in terminal

---

### Run the app

Build (or rebuild) the containers and run the app:
```
just build
```
- Do this if running for the first time, or any time after changing `pyproject.toml`, `Dockerfile`, or `.dockerignore` (or pulling in changes that touch those files)
- Good troubleshooting step to run this every now and then if things are unexpectedly breaking, especially if you're working with a new dependency

Run the app:
```
just up
```
- Edits to code files will reload automatically because of volume mounting, so no rebuild is needed for most code changes

Stop the app:
```
just down
```

API: http://127.0.0.1:8000  
Docs: http://127.0.0.1:8000/docs

---

### Run unit tests

Run the test suited (while the containers are running):
```
just test-backend
```
```
just test-frontend
```
```
just test
```

If you only want to run a specific test file or folder, add its path relative to tests/backend/ or tests/frontend/ to the end of the command, for example:
```
just test-backend test_services/
```

---

### Initialize, seed and inspect the database

Reset the development database (drop all tables, re-initialize, and re-seed all in one step).
```
just db-reset
```
- Run `just` to see commands for individual steps.

To inspect the database you have two options.
1. Use a GUI tool like [DBeaver](https://dbeaver.io/download/)
2. Enter an interactive Postgres CLI session:
```
just psql
```

> [!TIP]
>
> #### psql Tips
> 
> Some useful postgres commands to run in there:
> - List all tables: `\dt`
> - Get details of a table: `\d "TableName"`
> 
> You can also run SQL statements, terminated by semicolons:
> ```SQL
> INSERT INTO "Language" (name) VALUES ('Japanese');
> SELECT * FROM "Language";
> ```

---

### Make your IDE happy with a venv

> [!NOTE]
> This step needs Python 3.12 or later installed on your machine, with `python` available on your PATH.

In this project, the venv is **only for your editor**. It tells VS Code which packages and Python version we use, so you get tooltips and no false import errors. Don't use it to run the app or tests; those always run in Docker (the [docker_guard](./src/core/docker_guard.py) will stop you if you try).

Create (or re-create) a venv and install dependencies
```
just venv
```
- Rerun this every now and then if VS Code gives you weird import errors

Activate your venv by opening a fresh terminal in VS Code, or by running the activation script:
```
# On Mac/Linux
source .venv/bin/activate
```
```
# On Windows
.venv\Scripts\Activate.ps1
```

---

### Poke around (Advanced Commands)

These commands are deliberately not aliased in the justfile. Use them if you know what you're doing. Remember, in general, if you ever want to run modified versions of our common commands, the [justfile](./justfile) will tell you exactly what each alias runs under the hood.

Run any command inside the backend container:
```
docker compose exec backend <command>
```
- e.g. if you want to run `uvicorn` or `fastapi` commands other than the default startup command

Start an interactive shell:
```
docker compose exec backend bash
```
- if you need to run more than one command at a time, or poke around in there for some reason
- type `exit` to leave

---

## Project-Starter

> Please use the provided folder structure for your project. You are free to organize any additional internal folder structure as required by the project. 
> 
> ```
> .
> ├── docs                    # Documentation files
> │   ├── contract            # Team contract
> │   ├── proposal            # Project proposal 
> │   ├── design              # UI mocks
> │   ├── minutes             # Minutes from team meetings
> │   ├── logs                # Team and individual Logs
> │   └── ...          
> ├── src                     # Source files (alternatively `app`)
> ├── tests                   # Automated tests 
> ├── utils                   # Utility files
> └── README.md
> ```
> 
> Please use a branching workflow, and once an item is ready, do remember to issue a PR, review, and merge it into the master branch.
> Be sure to keep your docs and README.md up-to-date.
