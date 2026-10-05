# ENJIneers Language Game Project

This repo contains the source code for Team 9's Capstone Software Engineering project.

- [🔗 Team Contract](./docs/contract/team-contract.md)
- [🔗 Project Proposal](./docs/proposal/project-proposal.pdf)

### DFD level 1
[Game loop](docs/DFD/game-loop.md)
[Game Item Management](docs/DFD/game-item-management.md)

## How to run with fast api
1. Create a venv: `python -m venv .venv`
2. Activate it: `source .venv/bin/activate` (Windows: `.venv\Scripts\Activate.ps1`)
3. Install dependencies: `pip install -r requirements.txt`
4. Start the server: `fastapi dev src/main.py`
5. Check http://127.0.0.1:8000/docs

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
