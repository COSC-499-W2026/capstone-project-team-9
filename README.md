# ENJIneers Language Game Project

This repo contains the source code for Team 9's Capstone Software Engineering project.

## Links 

### Early Planning

- [🔗 Team Contract](./docs/contract/team-contract.md)
- [🔗 Project Proposal](./docs/proposal/project-proposal.pdf)

### System Design

- [🔗 System Architecture](./docs/system-design/system-architecture/system-architecture.md)
- [🔗 Data Flow Diagrams (level 0 and level 1)](./docs/system-design/data-flow-diagrams)
- [🔗 Database Design Documents](./docs/system-design/db-design)

## How to run with fast api
1. Create a venv: `python -m venv .venv`
2. Activate it: `source .venv/bin/activate` (Windows: `.venv\Scripts\Activate.ps1`)
3. Install dependencies: `pip install -r requirements.txt`
4. Start the server: `fastapi dev src/main.py`
5. Check http://127.0.0.1:8000/docs

## How to run with docker
Requires Docker Desktop to be installed and running.

First time, or after changing `requirements.txt` or the `Dockerfile`:

```bash
docker compose up --build
```

Every other time:

```bash
docker compose up
```

- API: http://127.0.0.1:8000
- Docs: http://127.0.0.1:8000/docs

Edits to files in `src/` reload automatically, so no rebuild is needed for code changes.

Rebuild with `docker compose up --build` after pulling changes that touch `requirements.txt` or the `Dockerfile`.

> ## Project-Starter
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
