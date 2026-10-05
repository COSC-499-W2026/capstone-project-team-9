Please note: This is a bit of a different log, because we are still very much in the preliminary system design stages of the project. For that reason, I am going to tell you about the work that I did, but I will not be following the regular log template since I did very little *coding* work.

# For PR [#26](https://github.com/COSC-499-W2026/capstone-project-team-9/pull/26):

Our system needs a relational database in which to store user, course, and game data persistently. Before this can be implemented in SQL, it needs to be designed conceptually and then logically.

For this reason I:
- carefully created an [Entity-Relationship diagram](../../system-design/db-design/ER-diagram.png), which describes database at a conceptual level.
- carefully created a [DrawDB visualization](../../system-design/db-design/drawdb-visualization.png), which moves the design closer to the actual Postgres implementation of the database; it includes info like data types, foreign keys, whether fields are nullable and relationship tables

The next step is to generate an actual PostgreSQL schema using DrawDB.

Using ER diagramming rules and then DrawDB foreign key constraints, I was able to ensure that there are no redundant tables, unneccessary columns, or overly convulated relationships. I also explained some of my non-obvious design choices in [db-design-choices-rationale.md](../../system-design/db-design/db-design-choices-rationale.md), which helped my reviewers understand and verify them.

The database design will continue to grow and change, but this is the solid base we needed to move forward in our database-related work. Joe gave me some good pointers on how we could implement scoring into the database soon.

--- 

Other important non-code PRs I worked on:



