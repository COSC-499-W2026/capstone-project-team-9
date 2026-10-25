# Individual Log - Week 5
Ian Steyn

## For PR [#44 Fix DFD names](https://github.com/COSC-499-W2026/capstone-project-team-9/pull/44):

> A mini-PR; regular template is not relevant here

In an effort to keep our repository clean and navigable, I performed some organizational changes to normalize filenames and clean up the README links for all the system design stuff we did last week.

I made sure to avoid breaking existing documentation by updating reference links to images and files anytime I updated the names of those images/files.

Related: my contributions to Nash's PR [#42 - DFD 0 Readme](https://github.com/COSC-499-W2026/capstone-project-team-9/pull/42), which I updated to match the new naming convention before merging it to `main`.

## For PR [#53 DB design - score and game state](https://github.com/COSC-499-W2026/capstone-project-team-9/pull/53):

> Summary: In this PR, I performed conceptual and logical database design updates to add the ideas of score and a saved game state to the database. 

> Associated issues:
> - [#30 Database design pt. 2 - add scoring & persistent saved games](https://github.com/COSC-499-W2026/capstone-project-team-9/issues/30)

### Score
As part of the requirement that _the system must record a player's score for each game played_, the database needs a field and associated entity in which to score store.

Therefore, I modified our Entity-Relationship diagram to include a new entity "Play", and modeled `Play` as a table in our visual database schema using DrawDB. A `Play` is a record of a **particular instance of a game**: it is associated with a particular player, and a score.

Reasoning for decisions made:
- `score` can't be added directly to a `Game` record, because games may be assigned to a course and thus played by multiple people.
- Another benefit of the `Play` approach is that it allows for the possibility of a single person replaying a particular `Game` more than once
- `score` is modeled a `NUMERIC` type because we have not yet come to a final decision on the details of score calculation, so we don't want to restrict it to `INTEGER`. If such a restriction is necessary at a later time, it is an easy change.

Addressing concerns and alternative approaches:
- When discussing this idea with Joe and Nash, we considered whether `score` should be associated with a particular `Course`, `Difficulty` or `Language` - since there will be "leaderboards" of some kind.
- However, I settled on `Play` because any combination of scores can be calculated from there. You can join and filter for scores from a particular game, course, language or difficulty, because a `Play` is associated with a `Game`, and a `Game` is associated a `Course`, `Language` and `Difficulty`. 

### Game State

As part of the user requirement that _players should be able to continue after pausing or disconnecting_, we identified a system requirement that _the system must save an in-progress game's state inbetween clues_.

Therefore, I modified our Entity-Relationship diagram to include a new many-to-many relationship between Clue and Play, and modeled it as a table `SolvedClue` in our visual database schema using DrawDB. The `SolvedClue` table **helps record the game state** by tracking which Clues have been solved by which Plays. The number of `SolvedClue` records associated with a particular `Play` also tells us whether or not the `Play` has been completed (i.e. have `Game.num_clues` been solved?).

Reasoning for decisions made:
- The main question was: what state do we actually need to save?
  - A `Game` is really just a **particular combination of rules** (language, difficulty, length) chosen by a creator at a particular time.
  - The list of Clues in a particular Play of a Game will be dynamically, randomly selected based on those rules.
  - So for any particular `Play`, the only state we need to save is _**which Clues have already been solved in this Play**_.
  - If a player pauses or disconnects after solving 4/10 clues, then continues at a later time, we can simply select a _new_ list of 6 clues, but make sure to _exclude_ any clues that have already been solved.
- Possible risks include: a player disconnects after having "solved" a clue, but before this is recorded in the database.
  - This risk can be mitigated by caching game state in the browser session before saving it to the database
  - But the *cost* here is low. At most, the player loses one solved clue; each solved clue serves as a "checkpoint" that saves your progress.

Addressing concerns and alternative approaches:
- The standard approach for saving complex game state is to write it in JSON and then serialize and store it as a single value in a SQL database.
- However, our game's state is simple enough to be modelled purely in SQL.

### General Notes on this PR

The PR does not contain any temporary workaround because I updated our design from the ground up, returning to the ER diagram to rethink our conceptual design, moving to the logical database design, and considering implications on foreign key constraints.

The reviews by Nash and Eric identified no problems.

This work is written in `docs/system-design/db-design/` because it is not directly tied to the code.
  - The ER diagram is now saved in `ER-diagram.drawio.png`, which makes it easily editable AND viewable
  - The visual schema can't be combined into a single file like that, so it is in `drawdb-visual-schema.json` (for re-import to DrawDB) and `drawdb-visual-schema.png` for visual import

As this is database design work, there is nothing to unit test in this PR.

---

## For PR [#56 Foreign key constraints + schema.sql Proof-of-Concept](https://github.com/COSC-499-W2026/capstone-project-team-9/pull/56)

> Summmary: In this PR I finished setting foreign key constraints for all relationships on the logical database design side, and generated a proof-of-concept SQL DDL script using DrawDB.

> Associated Issues:
> - [#7 Database Schema](https://github.com/COSC-499-W2026/capstone-project-team-9/issues/7)

### Foreign key constraints

As part of our requirement to persistently store data in a database, we need to ensure that updates to data propagate to related data in a safe, well-defined manner. These constraints are closely tied to the conceptual modelling I did in the previous PR, and applying them to our current logical design is the last step needed before our SQL schema is ready.

Therefore, I went through every foreign key in DrawDB and checked its `ON UPDATE` and `ON DELETE` actions. I verified that I checked every key by adding a ✅ to each relationship name in DrawDB after checking it.

<details><summary>Click here to see the details of how delete and update behaviour will work it in the updated design, and the "why" for each of my decisions:</summary>

- If a `User` is deleted:
  - resources they created (Clues, Targets, Games) or own (Courses) set `creator_id` or `owner_id` to `NULL`
    - Why: Resources and courses can exist without a creator. They only have a creator_id so that instructors can only edit resources they created.
  - their Plays are deleted (and so are the associated SavedClues)
    - Why: Plays and SavedClues record a player's history. If the player is gone, their history is unimportant.
  - their Enrollments are deleted
    - Why: Enrollments are purely a junction table. If one end of the relationship doesn't exist, enrollments are meaningless.
- If a `Course` is deleted:
  - associated Enrollments are deleted
    - Why: Enrollments are purely a junction table. If one end of the relationship doesn't exist, enrollments are meaningless.
  - associated Games set `course_id` to `NULL`
    - Why: so that players can retain score data
- If a `Game` is deleted:
  - associated Plays set `game_id` to `NULL`
    - Why: so players can retain score data
- If anything else is deleted:
  - the deletion will only succeed if there are no associated records elsewhere in the database
    - Why: More nuanced delete behaviour can be considered in future (see issue [#54](https://github.com/COSC-499-W2026/capstone-project-team-9/issues/54)) , but this is safest for now
- All `ON UPDATE` actions are set to `RESTRICT`
  - Why: all foreign keys are numerical ids and updating them just shouldn't happen

</details>

### Generated SQL schema

Finally, I added an actual PostgreSQL DDL script, generated by DrawDB based on the work I did on the visual schema.

The script is not intended to be functional right now. It's just a proof-of-concept to:
1. Show the foreign key constraints (since you can't see them on the visual schema PNG)
2. Show what the visual schema looks like as actual SQL, and understand how DrawDB generates SQL

When I reviewed the generated script, I did not find any problems with it because:
- DrawDB has a built-in "problem checker" that notifies you of logical errors or inconsistencies; I fixed all of these before exporting the SQL (except for one, but this appears to be a [known bug](https://github.com/drawdb-io/drawdb/issues/1144) with how DrawDB evaluates default values for Postgres `TEXT` fields)
- DrawDB escapes all table and field names using quotes
- One non-issue: DrawDB adds a separate `ALTER TABLE` statement for each foreign key, but with the small size of our database (and the infrequency of actually having to initialize it), the cost to performance is negligble

### General notes on this PR

This PR does not contain any temporary workarounds because the SQL script, while not in use in its current form, serves a design-related purpose rather than that of a temporary bootstrap.

The SQL script is written in `db/schema.sql` because the database initialization script is separate from the actual application code in `src/`. Other DB scripts will go in this folder in the future.

As this is database design work, there is nothing to unit test in this PR.

---

## For PR [#63 Add new requirements and timeline document](https://github.com/COSC-499-W2026/capstone-project-team-9/pull/63)

> Not a technical PR, doesn't really make sense to follow the template

> Associated issues:
> - [#51 Project Roadmap and Task Breakdown](https://github.com/COSC-499-W2026/capstone-project-team-9/issues/51)

Sadia asked us to do more planning and goal-setting this week, so Nash and I met to do so. We didn't meet as a full team, because not everyone was as available over Thanksgiving weekend, and also Nash and I are the most planning-oriented members of the team. We rewrote all our requirements as functional system requirements using the formal "The system shall" language, and grouped them by feature area. We gave each requirement a "short name", to make them easy to read and to later translate directly to parent issues on our project management board.

We also sketched out a rough timeline for the rest of the term, set some goals for what we wanted to achieve by the end of each week in the term, and what our vision is for the end of Milestone 1 and end of Milestone 2. 

This work will help us prepare well for the weeks ahead, as it gives us a clearer idea of where we are headed and what we need to accomplish week-to-week.

I documented this work in `docs/proposal/new-reqs-and-timeline.md` based on notes from our meeting. The next step is to put it all into our project board.

---

## Other non-PR things I did this week
- Did [#48 Add labels and milestones to issues](https://github.com/COSC-499-W2026/capstone-project-team-9/issues/48) to help us organize and properly prioritize our work. See:
  - [project board](https://github.com/orgs/COSC-499-W2026/projects/2/views/1)
  - [repo labels](https://github.com/COSC-499-W2026/capstone-project-team-9/labels)
  - [repo milestones](https://github.com/COSC-499-W2026/capstone-project-team-9/milestones)
- Updated meeting minutes (see [docs/minutes/meeting-minutes.md](https://github.com/COSC-499-W2026/capstone-project-team-9/blob/main/docs/minutes/meeting-minutes.md))
- Reviewed PRs: [#57](https://github.com/COSC-499-W2026/capstone-project-team-9/pull/57), [#55](https://github.com/COSC-499-W2026/capstone-project-team-9/pull/55), [#39](https://github.com/COSC-499-W2026/capstone-project-team-9/pull/39), [#58](https://github.com/COSC-499-W2026/capstone-project-team-9/pull/58)
