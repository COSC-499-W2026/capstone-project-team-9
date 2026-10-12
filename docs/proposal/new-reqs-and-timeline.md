# New requirements and timeline

## **Functional System Requirements**

#### **USER ACCOUNTS**

- **\*Sign-up:** The system shall allow user to sign up with name, email and password  
- **\*Log-in:** The system shall authenticate users attempting to log in by verifying their email and password   
- **Password encryption:** The system shall encrypt user passwords using a strong hashing algorithm.  
- **Email encryption:** The system shall encrypt user emails at rest in the database.  
- **Edit profile:** The system shall allow an authenticated user to update name, email, and password  
- **(milestone 2\) Achievements:** Bruh

#### **GAME LOOP**

- **\*Custom game creation**: The system shall allow any user to create a game with a particular difficulty, language, length  
- **\*Start a Play:** The system shall generate an instance of a game, selecting a random combination of clues that match the game’s ruleset.  
- **\*End a Play:** The system shall allow a user to end an instance of a game at any time.  
- **\*Location check:** The system shall verify that the user’s location in on campus before starting the game loop.  
- **Save game state**: The system shall save an in-progress play’s current state after each task, in case the user pauses or disconnects.  
- **Pause Play**: The system shall allow an in-progress game to be paused.  
- **Continue Play**: The system shall allow a user to continue a previously paused game

#### **GAME TASKS**

- **Clues**  
  - **\*Play audio Clue:** The system shall play an audio clue for the player.  
  - **\*Replay audio Clue:** The system shall allow the user to replay an audio clue any number of times.  
- **Targets**  
  - **\*Upload image:** The system shall allow the user to take and upload an image for a clue.  
  - **\*Evaluate image:** The system shall compare an uploaded image with the clue target and evaluate whether it is correct using ML/image processing tools.  
- **Skipping and multiple attempts**  
  - System allows user to make X attempts  
  - System retrieves and provides hint and/or slowdown audio after X attempts  
  - System allows user to skip to next item after X attempts  
- **(milestone 2\) Success audio:** After item:System plays specified success audio

#### **SCORING**

- **Individual clue score**: The system shall calculate a score for each solved clue  
- **Total play score**: The system shall calculate and store a total score for each game  
- **Get Scores:** The system shall allow an authenticated user to retrieve their past game scores

#### **Courses (instructor)**

- **View courses:** The system shall display a list of a user’s enrolled courses  
- **Create courses:** The system shall allow instructors to create a course with a default language  
- **Enrollment on course creation:** The system shall auto-enroll the course creator  
- **Course Owner:** The system shall allow the course creator to switch ownership of the course to another enrolled user  
- **Course enrollment:**  
  - **Course access code:** The system shall generate a simple alphanumeric access code for each course with which users can enroll  
  - **Enroll:** The system shall allow users to enroll in a course by entering an access code  
  - **Unenroll:** The system allows students to unenrolled/leave a course  
- **Course student management**  
  - **View students:** The system shall display a list of all enrolled users to course instructors  
  - **Unenroll students:** The system shall allow the instructor to unenroll/remove students from a course  
  - **TA permissions:** The shall System allows owner to give enrolled users instructor permissions specific to that course  
- **Create assigned game:** The system shall allow instructors to create games with a due date, and assign them to a course  
- **View assigned games:** The system shall display a list of all assigned games in a course to all enrolled users  
- **Course Leaderboards:** The system shall display a list of all student scores aggregated to all enrolled users  
- **Course score export:** The system shall allow instructors export all student scores in a course to a CSV file

#### **GAME RESOURCES**

- **Target operations**  
  - **Create targets:** The system shall allow the instructor to add a new target with a name and image, and will warn them if the target already exists  
  - **Target creation validation:** The system shall warn the instructor if the newly created target already exists in the database  
  - **Edit and delete targets:** The system shall allow instructors to edit and delete targets they have created, and allow admins to edit and delete any targets.  
- **Clue operations**  
  - **Create Clues:** The system shall allow the instructor to add a new clue with an audio file, language and difficulty, and target (chosen from language/difficulty/target already in the system).  
  - **Clue creation validation:** The system shall warn the instructor if a clue with the same language, difficulty and target already exists in the database  
  - **Edit and delete targets:** The system shall allow instructors to edit and delete targets they have created, and allow admins to edit and delete any targets.  
- **Language operations:**  
  - **CRUD languages**: The system shall allow only the admin to Create, Update and Delete all languages  
- **Difficulty operations:**  
  - **CRUD difficulties:** The system shall allow only the admin to Create, Update and Delete all languages

#### **ADMIN**

- **Admin user operations**  
- **Read all users:** The system shall display a list of all users to the administrator  
- **Change user roles:** The system shall allow an admin to change any user’s role/permission level  
- **Delete users:** The system shall allow an admin to delete any user.  
- **Admin course operations**  
  - **Admin CRUD courses:** the system shall allow the admin to create, read, update and delete all courses as if they were the owner of all of them.

---

## **Rough Timeline**

#### **Milestone 1** 

END-OF-TERM GOAL: A functional version of the core game, user accounts, instructor and admin interfaces, with a minimal but functional backend.

* WEEK 3 \- Due: proposal  
* WEEK 4 \- Due: system design diagrams  
* WEEK 5 \- \[we are here\]  
* WEEK 6 \- (lots of midterms) \- focus on further config and familiarization  
* WEEK 7 \- Goal: have a basic Vue front-end setup  
* WEEK 8 \- SUB-MILESTONE A.  
  * Goal: Basics structures in place \- login, game loop, game tasks, scoring  
* WEEK 9 \- focus on refining and testing basic structures  
* WEEK 10 (midterm break: grind time) SUB-MILESTONE B  
  * Goal: secondary structures in place \- courses, leaderboards, instructor/admin CRUD  
* WEEK 11 \- focus on refining and testing secondary structures  
* WEEK 12 (milestone 1 due end of week) \- overflow  
* Week 13 \- (presentations)

#### **Milestone 2**

END-OF-TERM GOAL: A polished, fun, maintainable version of the game, ready to be passed off to the client.

* UI mockups/design  
* Full front-end implementation  
* User experience testing  
* \+  
* Gamification features: achievements, themes, artistic assets  
* Bonus features: custom group games
