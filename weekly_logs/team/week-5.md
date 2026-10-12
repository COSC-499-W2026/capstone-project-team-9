## Week 5 Team log

This week, we decided to focus on further planning and research (as directed by Sadia), as well as more project configuration, learning how to work with FastAPI, and database design, all with the goal of getting a more solid foundation for the project and a clearer idea of what we need to do in the weeks ahead.

The work was distributed so that:
- Joe focused on adding and testing an API endpoint for verifying location (PRs: #57, Issues: #52)
- Eric focused on researching image processing technologies (PRs: #59. Issues: #50)
- Nash focused on configuring a pyproject.toml file, improving the repository organization, and working with Ian to redefine requirements and goals (PRs: #39, #58. Issues: #45, #51)
- Ian focused on progressing the database design, creating a SQL schema, improving the project management and repository organization, and working with Nash to redefine requirements and goals (PRs: #44, #53, #56, #63. Issues: #7, #30, #47, #48)

We considered alternative workload distributions such as every member adding an API endpoint, but several members ran out of time and did not complete all tasks that were assigned at the end of the week (it was Thanksgiving weekend).

However, based on the fact that all of the above PRs were merged and issues completed, we met our goal; we now have a reorganized set of clear system requirements, a rough timeline for the rest of the milestone, and a definition of a Minimum Viable Product (`docs/proposal/new-reqs-and-timeline.md`, #53). We also have...
- An improved understanding of our technologies:
  - We have a research document on image processing choices (`docs/system-design/image-processing/research.md`, #57)
  - The new API endpoint is a good working example for other teammates to understand FastAPI routes, services, repos, schemas and tests in future weeks build many more endpoints (#52)
- A more organized project
  - Our Python code is more organized due to a `pyproject.toml` file (#39)
  - Our project management is more organized due to new labels and mini-milestones (#30)
- A clearer model of entities and relationships in our system
  - (see more on updated DB design docs below)

The team collectively reviewed all technical pull requests with two reviewers, implemented clean FastAPI development practices, and checking our DFDs/system architecture when developing to ensure that the code base does not contain any of the following:
 - similar logic implemented multiple times
 - many dependencies between modules
 - changes in one component require changes elsewhere

(There was a particular case where Ian reviewed Joe's PR #57 and found issues with "repo" logic being injected into "routers" as a dependency, but Joe fixed this problem and the PR was merged with clean separation of concerns.)

With everyone's newly merged work for this week, the system DFDs look like the same. However, Ian's database design work has caused updates to the ER diagram and visual database schema. Visual diffs can be seen in [PR #53](https://github.com/COSC-499-W2026/capstone-project-team-9/pull/53). The specific changes include new concepts of "plays", scoring and saved game state. We considered alternative relationships such as a direct connection between Clues and Games, but a more indirect connection was deemed necessary for one game to be available to multiple players (as per the requirements).

With everyone's newly merged work for this week, the system architecture diagram looks the same. We are still considering specific image processing libraries based on Eric's research, and will update our "official" architecture diagrams once his research has been discussed with the whole team.

---

This week's team log was authored by: Ian Steyn