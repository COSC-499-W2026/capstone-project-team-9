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

- [Run the app](#run-the-app)
- [Run unit tests](#run-unit-tests)
- [Poke around in the container](#poke-around-in-the-container)
- [Make your IDE happy with a Venv](#make-your-ide-happy-with-a-venv)

> [!IMPORTANT]
> #### Using Docker
> Our app and tests must be run inside a **Docker container** to ensure that our environments and dependency versions are identical at all times. Our CI runs the test suite in a container built from the same image.
> 
> _**You will need Docker Desktop to be installed and running.**_

> [!TIP]
> #### Terminal Tips: tired of retyping long commands?
> - use the `↑` up arrow key to cycle through previous commands
> - use the `tab` key to cycle through files and directories

---

### Run the app

Build (or rebuild) the container and run the app:
```bash
docker compose up --build
```
- Do this if running for the first time, or any time after changing `pyproject.toml`, `Dockerfile`, or `.dockerignore` (or pulling in changes that touch those files)
- Good troubleshooting step to run this every now and then if things are unexpectedly breaking, especially if you're working with a new dependency

Run the app:
```bash
docker compose up
```
- Edits to code files will reload automatically because of volume mounting, so no rebuild is needed for most code changes

API: http://127.0.0.1:8000  
Docs: http://127.0.0.1:8000/docs

---

### Run unit tests

Run the test suite (while the container is running):
```
docker compose exec backend pytest
```
If you only want to run a specific test file, just add the relative filepath from `tests/` to the end of the command above.

---

### Poke around in the container

Run any other command inside the container:
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

### Make your IDE happy with a venv

> [!WARNING]
>
> In _this_ project:
> - you do not need a venv to run the app or tests
> - you should not use a venv to run the app or tests
>   - If you do so accidentally, the [docker_guard](./src/utils/docker_guard.py) should stop you
> 
> But you _should_ use a venv...
> - ...to keep your code editor and linter happy! It's basically a way of telling VS Code what packages and Python version you are using so it can give you helpful tooltips and not freak out about import errors.
> - ...to stop yourself from accidentally messing with your global Python environment and affecting other Python projects on your laptop

1. Create a venv
```
python -m venv .venv
```
2. Activate it:  
```
# On Mac/Linux
source .venv/bin/activate
```
```
# On Windows
.venv\Scripts\Activate.ps1
```
3. Install dependencies:
```
python -m pip install e ".[test]"
```
- Rerun this every now and then if VS Code gives you weird import errors

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
