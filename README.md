# Project-Starter
Please use the provided folder structure for your project. You are free to organize any additional internal folder structure as required by the project. 

```
.
├── docs                    # Documentation files
│   ├── contract            # Team contract
│   ├── proposal            # Project proposal 
│   ├── design              # UI mocks
│   ├── minutes             # Minutes from team meetings
│   ├── logs                # Team and individual Logs
│   └── ...          
├── src                     # Source files (alternatively `app`)
├── tests                   # Automated tests 
├── utils                   # Utility files
└── README.md
```

Please use a branching workflow, and once an item is ready, do remember to issue a PR, review, and merge it into the master branch.
Be sure to keep your docs and README.md up-to-date.

Team Contract: https://docs.google.com/document/d/1GHIV5elR9nJ73-4lpqKuxXhP2SIJv0zbS5vYA-md0HA/edit?usp=sharing
Project Proposal: https://docs.google.com/document/d/1gdP1ezxP8H3JWAgSC37RRSwbDzWlVQ30cE4rTG8Ly1o/edit?usp=sharing


## How to run with fast api
1. Create a venv: `python -m venv .venv`
2. Activate it: `source .venv/bin/activate` (Windows: `.venv\Scripts\Activate.ps1`)
3. Install dependencies: `pip install -r requirements.txt`
4. Start the server: `fastapi dev src/main.py`
5. Check http://127.0.0.1:8000/docs