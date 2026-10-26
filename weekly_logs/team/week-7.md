## Weekly Team Log

This week, we decided to focus on improving the project's database integration, reorganizing the system architecture, implementing custom game functionality, and improving user registration and answer verification, with the goal of making the system more reliable, modular, and functional.

The work was distributed so that:
- **Nash** focused on refactoring the user endpoints, removing unnecessary ID assignments (PR #140https://github.com/COSC-499-W2026/capstone-project-team-9/pull/140), integrating the user model and repository with the database, writing separate repository, router, and service tests (PR #152https://github.com/COSC-499-W2026/capstone-project-team-9/pull/152), and improving password security using bcrypt (PR #157https://github.com/COSC-499-W2026/capstone-project-team-9/pull/157).
- **Ian** focused on introducing SQLModel-based database initialization to reduce duplicated schema definitions (PR #142https://github.com/COSC-499-W2026/capstone-project-team-9/pull/142), moving the Docker guard into the core directory (PR #143https://github.com/COSC-499-W2026/capstone-project-team-9/pull/143), and separating the frontend and backend into distinct directories with updated configurations and CI workflows (PR #147https://github.com/COSC-499-W2026/capstone-project-team-9/pull/147), and implementing database seeding and resetting scripts with environment safeguards (PR #158https://github.com/COSC-499-W2026/capstone-project-team-9/pull/158).
- **Joe** focused on implementing the game configuration endpoints for languages, difficulties, and game lengths (PR #148https://github.com/COSC-499-W2026/capstone-project-team-9/pull/148), as well as the endpoint for starting a custom game with the selected settings (PR #151https://github.com/COSC-499-W2026/capstone-project-team-9/pull/151).
- **Eric** focused on implementing target location verification for photo-based challenges (PR #150https://github.com/COSC-499-W2026/capstone-project-team-9/pull/150) and developing the answer-checking service that combines location verification and OCR to determine whether a submitted answer is correct (PR #155https://github.com/COSC-499-W2026/capstone-project-team-9/pull/155).

We considered alternative workload distributions, such as having every team member work on separate API endpoints or assigning all database-related tasks to one person. However, dividing the work by feature and technical responsibility allowed team members to develop components independently while maintaining clear interfaces between us. This also allowed infrastructure changes, game functionality, and user authentication improvements to progress in parallel.

Based on the successful merging of the listed pull requests and the addition of corresponding tests, we made progress toward our goals. The project now has improved database initialization, a clearer separation between the frontend and backend, working endpoints for configuring and starting custom games, and additional services for validating answers. User registration has also been connected to the database, with bcrypt improving password security.

In particular, Ian's PR #158https://github.com/COSC-499-W2026/capstone-project-team-9/pull/158 added scripts for seeding development data, seeding reference data, and resetting the database. A shared helper module reduces the need to duplicate seeding logic, while the new ENV environment variable restricts potentially destructive database operations to the development environment. These changes make it easier to prepare a consistent database for development and testing.

Some components still require further integration and testing. For example, the answer-checking service does not yet have an API endpoint, and the database initialization process still requires manual verification. 

The team collectively reviewed the new components and interfaces to reduce the risk of duplicated logic, unnecessary dependencies, and changes in one component requiring changes elsewhere.

- **Reducing duplicated logic:** Ian introduced SQLModel-based database initialization to avoid maintaining separate Python models and SQL schema definitions as competing sources of truth (PR #142https://github.com/COSC-499-W2026/capstone-project-team-9/pull/142). He also created a shared helper module for logic used by both database seeding scripts (PR #158https://github.com/COSC-499-W2026/capstone-project-team-9/pull/158). Eric also reused the existing distance-calculation function for both campus and target location verification (PR #150https://github.com/COSC-499-W2026/capstone-project-team-9/pull/150), avoiding duplicated geographic calculations.
- **Reducing dependencies between modules:** Eric designed the answer-checking service so that it coordinates location verification and OCR without making either service directly depend on the other (PR #155https://github.com/COSC-499-W2026/capstone-project-team-9/pull/155). This keeps the individual services independent and makes their functionality easier to test.
- **Improving separation of concerns:** Ian reorganized the project to separate frontend and backend code, configurations, and CI workflows (PR #147https://github.com/COSC-499-W2026/capstone-project-team-9/pull/147). He also moved the Docker guard into the core directory because it is an infrastructure tool (PR #143https://github.com/COSC-499-W2026/capstone-project-team-9/pull/143). Nash maintained separate repository, router, and service tests for user registration (PR #152https://github.com/COSC-499-W2026/capstone-project-team-9/pull/152), helping preserve clear boundaries between database operations, API handling, and business logic.
- **Improving database safety:** Ian added an ENV environment variable to restrict potentially destructive database operations to the development environment (PR #158https://github.com/COSC-499-W2026/capstone-project-team-9/pull/158). This helps reduce the risk of accidentally resetting or modifying a database in another environment.

These changes improve modularity and reduce unnecessary dependencies. However, the team will need to continue reviewing the code as the services are integrated to ensure these principles remain consistent throughout the codebase.

With everyone's newly merged work for this week, the system DFDs look the same.

With everyone's newly merged work for this week, the system architecture diagram looks the same.

- - -

This week's team log was authored by: Nash Lovegren