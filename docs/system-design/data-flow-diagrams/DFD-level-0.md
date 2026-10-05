### DFD level 0
![ DFD level 0](images/Level-0-DFD.png)

**Purpose:** This shows the system at a high level.

**Processes**
- 1 Game loop: allows users to play the game without needing to log in to an account.
- 2 Login: gets log in information to let users access their dashboards and scores.
- 3 Student management: verifies correct account type, and gives related student information.
- 4 Class management: generated and stores class codes, and edits enrolled students.
- 5 Student dashboard: shows logged in users classes, scores, and allows class management like joining or leaving a class.
- 6 Game loop (Logged in): allows users to play the game, and saves their scores to their account.

**Data stores**
- Account information: username, password, enrolled classes, scores 
- Class information: students in a class, class scores
- Game Iteam: locations, images, and audio clues