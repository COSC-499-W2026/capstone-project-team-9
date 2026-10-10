# Rationale behind some non-obvious DB design choices
by @iansteyn

## Users and their relationships

### `User.role` and `Enrollment.is_course_instructor`

-  All users are stored in a single `User` table, with the `role` column (either `"student"`, `"instructor"` or `"admin"`) determining their overall permissions
- So why is there also a boolean attribute `is_course_instructor` in the Enrollment relationship?
  - Because I think courses should have a single owner (see below)... but there may be cases when multiple instructors are teaching a course, or the main instructor wants TAs to do grading, etc. In such cases, secondary instructors would simply enroll in the course like regular students, and the main instructor would be able to give them instructor permissions _for that specific course_

### Which entities can be created by users, and by which roles?

- **instructors** can do CRUD operations on **games**, **clues** and **answers**. 
  - Each of these have a `creator_id` so that an instructor can only do RUD on entities they created.
  - `creator_id` is _nullable_ in case the creator's account is deleted - in this case admins will still be able to manage these entities
- I think only **admins** should be able to manage **languages** and **difficulties**
  - since admins can edit everything, no need for a specific `creator_id`, `created_at` or `updated_at` on these entities
- Instructors/admins can also do CRUD ops on **courses**
  - HOWEVER there should always be someone with instructor access to the course, so instead of a nullable `creator_id`, I've given `Course` a mandatory `owner_id` - by default this would be the course's creator, but that instructor would be able to pass it off to someone else if necessary.

## Game state

Our requirements state that players should be able to:
> - Pause game, resume game
> - Have game save state after each level, in case of disconnect

### What state do we actually need to save?
Apparently when you get into saving complex game state in SQL, people tend to just save a bunch of it in JSON and then serialize it into a string or `JSONB` that gets stored as a single value in SQL. However, I think we can get away with regular old SQL for our case.

- Recall: Each game consists of a set of random levels (or "clues").
- The only state we really need to save for a particular "instance" or "play" of a game is _which levels have already been completed_
- Then, to re-start the game, all we need to do is re-generate a smaller version of the game, excluding the already-completed levels from the set of available levels to randomly pick from.

### Understanding the different Game entities

In the database:
- A `Game` is really just a **particular combination of rules** (language, difficulty, length) chosen by a creator at a particular time. It may be assigned to a course and thus played by multiple people, or it may be a one-off created by a single user for a one-time play. 
- A `Play` is a record of a **particular instance of a game**: it is associated with a particular player, and a score.
- A `CompletedClue` helps **record the game state** by associating `Clue`s with `Play`s.