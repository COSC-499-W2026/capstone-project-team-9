For PR #59:

 As part of requirement Research and Select Image Processing Solution, the user needs to hear the audio of a room number, find that room, take an in-app camera photo of the door, and submit it so the system says right or wrong.

 Therefore, I researched and documented the image processing approach (OCR for reading the door plaque and an OpenCV SIFT + RANSAC scene check against the reference photo) so that students using the language-learning app get an accurate right/wrong result from photos taken at any distance or angle. No code was implemented in this PR.

 When I reviewed the research notes (OCR and Scene Check Notes) for this functionality, I noticed no issues. My biggest set back was just trying to figure out which option would preform the best without being able to test it. To solve this i read a bunch of users reviews from each and choose the one which seemed to have the least issues and fit our requiremtns the best.

 The PR does not contain any temporary workaround because it does not contain code logic. It contains research notes that recommend long-term solutions.

 I did review the notes against our requirements (free tooling, any image size/quality, camera-only capture) to ensure that the recommended approach does not lead us into any of the following:
 - hardcoded values
 - duplicate code
 - dead code
 - unnecessary function calls
 - excessive conditional logic
 - deep nesting
 - high cyclomatic complexity
 - classes/modules/functions with many unrelated responsibilities
 Specifically, the notes warn against hard-coding the room code length and recommend validating against the real room list and tuning the match threshold on real photos instead of guessing a fixed value. No code exists yet to check for the other items.

 This work is written in docs/system-design/image-processing/research.md because research documentation belongs in the docs folder and not in the backend source.

Test receipts: no tests were written in this PR because it contains research only and no code. The sections below are not applicable.