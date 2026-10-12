# Meeting minutes

> **Key**
> 
> 🏫 = lecture/check-in  
> 🔴 = proper in-person meeting / work-block  
> 📱 = discord check-in / call  

## Week 1

_No notes. Team not yet formed._

---

## Week 2

### 🏫 Tue, Sept 15

**Time:** 12:30–1 PM  
**Location:** In Lecture  
**Attendees:** Ian, Joe, Nash, (Eric sick)

#### Notes:

- Agreed on Scavenger hunt project option

#### Actionables:

- Come to next meeting\!

---

### 🔴 **Wed, Sept 16**

**Time:** 1 \- 2:30 PM  
**Location:** EME 1162  
**Attendees:** all

#### Agenda:

- team contract  
- Discuss expectations, get to know each other  
- Setup github kanban board  
- Discuss project ideas/interests/motivations at a high level

#### Notes:

- General values and expectations  
- Filled out team contract  
- Discussed project topic \- tentatively choosing Language game, still considering GPS project

#### Actionables:

- Clean up team contract, get it signed and handed in  
      - Nash  
- Join github repo  
      - Everyone  
- Make github kanban board  
      - Ian

Coming up soonish

* System architecture & data flow diagram  
* Requirements  
* proposal

---

### 🏫 Thurs, Sept 17

**Time:**  12:30–1 PM  
**Location:** lecture  
**Attendees:** all

#### Agenda:

- Learn about DFD stuff and system architecture  
- If there are any further to-dos, assign to Eric and Joe

#### Notes:

- Both classes next week are client meetings  
- DFD due in 2 weeks  
- Ian will not be present for client meeting on Thursday the 24th

#### Actionables:

- Start thinking about and writing down functional requirements  
      - Everyone

---

## Week 3

### 🏫 Tues, Sept 22

**Time:**  12:30–1 PM  
**Location:** Online  
**Attendees:** Ian

#### Notes:
- took notes on Youry's project on behalf of the team

---

### 🔴 **Wed, Sept 23**

**Time:**  11–1 PM  
**Location:** EME 2252  
**Attendees:** all

#### Agenda:

- Questions for our client  
- Discuss last client meeting  
- Todos for the weekend/sunday hand-in

#### Notes:

- Discusses Youry’s project and finalized project topic choice: game project  
- Reviewed user profiles, requirements, project brief \- came up with list of questions for client  
- Reviewed Proposal to-dos  
- Brainstormed value proposition  
- Set day to work on Project Proposal

#### Da plan:

- Next class: Eric, Joe, Nash attend Client meeting, take notes, answer our questions  
- Everyone: do some research on potential tech stacks and come to next meeting with some suggestions

---

### 🏫 Thurs, Sept 24

**Time:**  12:30–2 PM  
**Location:** lecture  
**Attendees:** Eric, Joe, Nash (Ian away for wedding)

#### Agenda:

- Attend Client Session  
- Answer our questions  
- Research tech stacks

#### Notes:

- meeting successful. Full notes in Google Drive.

---

### 🔴 **Sat, Sept 26th**

**Time:** 11am - 5pm  
**Location:** EME 1164  
**Attendees:** all

#### Agenda:

- Team name
- Review client meeting
- Clarify requirements 
- Formalize requirements and put them into work breakdown structure  
- Review Tech Stack research 
- Select tech stack
- Write project overview  
- Value proposition

#### Notes:

- picked a proper team name: _**The ENJIneers**_
- completed all agenda items (see above)
- discussed tech stack beyond what is on proposal
- handed in proposal

#### Actionables:

- chill until next class, we deserve it :)

---

## Week 4

### 🏫 Tues, Sept 29

**Time:**  12:30-1 PM  
**Location:** In Lecture  
**Attendees:** Ian, Joe, Eric (Nash sick)  

#### Notes:
- discussed system architecture at a high level with Bowen and other game teams

#### Actionables:
- Eric: setup Pytest
- Joe: setup FastAPI boilerplate
- Ian: DB spec/design
- Nash: if ur super sick, just be sick. Or if you can, do more tech stack research.

---

### 🏫 Thurs, Oct 1

**Time:**  12:30-1 PM  
**Location:** In Lecture  
**Attendees:** Ian, Joe, Eric (Nash sick)  

#### Notes
- put tasks in Kanban board
- Ian showed DrawDB tool
- brainstormed further PRs that could be completed this weekend

---

### 🔴 **Friday, Oct 2**

**Time:**  11-1 PM  
**Location:** EME 2254  
**Attendees:** Ian, Joe, Eric (Nash sick)  

#### Agenda
- develop high level System Architecture as a group
- identify components and assign data flow diagrams
- review further todos (PRs, logs, evals, etc)

#### Notes
- discussed progress on actionables (db design, fastAPI setup, and pyTest setup all almost done)
- worked through system architecture on whiteboard
  - investigated data abstraction layers: ORM/SQLModel, FastAPI `models/` vs `repositories/`
  - investigated using `oAuth2` with FastAPI
- identified "major processes" - for level 1 data-flow diagrams
- worked through rough drafts for: DFD level 0, DFD level 1 for game loop, login and game item management

#### Actionables
- Before Sunday night...
  1. Put in and review Pull Requests for stuff that is already almost done (db design, fastAPI setup, pyTest setup, docs)
  2. finish diagrams (assigned on project board)
  3. do further PRs/coding tasks if time allows (Docker, DB Schema, Coverage.py)
  4. Do team and individual logs

---

## Week 5

### 🔴 Tues, Oct 6

**Time:** 12:30-1:30  
**Location:** ~~COM 314~~ Picnic bench outside COM  
**Attendees:** all

#### Agenda

- Review last week’s workflow  
  - How can we do this sustainably?  
  - Suggestions for logs  
  - PR review practices  
- Review proposal feedback  
- Prep for check-in: how is everyone’s understanding of…  
  - Fastapi & system arch  
  - Pytest & CI  
  - Venv and Docker  
  - DB design  
- Diagrams  
- Assign todos for this sprint

#### Notes:

- Reviewed last week’s workflow:  
  - Things will get better as we get into the rhythm of things  
  - We should ask about logs for non-code work at the meeting  
  - Reminder to everyone to properly comment on and review PRs  
  - Decided we are moving our meetings to Tuesdays at 12:30 \- Joe will book a room every week  
  - Nash is moving our groupchat to a Discord Server  
- Reviewed Proposal feedback  
  - Most of it is meh, the only important one to keep in mind is that the instructors are iffy on Canvas LTI integration  
- Reviewed system and made sure everyone knows what is going on  
  - FastAPI and system arch \- Nash should review since he wasn’t there on Friday  
  - Pytest & CI \- ian mentioned we can run our CI tests on more OSs, maybe something to think about for future  
  - Venv, Docker and Pyproject \- Joe walked everyone through the dockerfile, but there is more investigation/understanding to be done here  
  - DB design \- Ian shared some core concepts of the current DB design, group discussed how scores will fit in  
- Note on diagrams  
  - For future: everyone should save diagrams as `diagram.drawio.png`, which saves XML diagram setup directly to the png and makes them easy to edit for other people  
- Assigned initial todos for this sprint. Overall:  
  - Prioritize database setup  
  - Improve devops/environment setup  
  - Implement simple API endpoints

#### Actionables

- All: move system requirements into project board as issues
- Ian: look into venv/docker  
- Ian: DB schema \+ postgres setup  
- Joe: GPS / location check endpoint  
- Joe: at least 1 more endpoint  
- Eric: Coverage reporting  
- Eric: start looking into FAST API signup/login and OAuth tools?  
- Nash: Pyproject.toml  
- Nash: API endpoint

---

### 🏫 Thurs, Oct 8

**Time:**  12:30-2 PM  
**Location:** In Lecture Check-in 
**Attendees:** Ian, Joe, Eric, Nash

#### Agenda
- TA Check-in

#### Notes
1st check-in with TA Sadia
- Reviewed proposal feedback
  - asked for +1 mark on tech stack choice
  - discussed reset/shuffle
  - discussed Python image processing library - Sadia wants us to choose this
- Discussed Milestone 1 vs 2 - Sadia wants us to have a clearer idea of what our goals are by the end of this milestone
  - She says if we make it clear in our logs that we did project management work, she will be lenient with the "2 PRs" rule for this next week (because of her specific feedback)
  - She also says we will need *some* kind of front end in milestone 1 due to the nature of the project, even if it is super basic and ugly
- Some team discussions of what we want to do by end of term and how to get there:
  - basically, we want a game that works
- everybody recognized we have a bit lower capacity rn because of Thanksgiving weekend + midterms this/next week

#### Actionables
Mostly same as before, except:
- Ian & Nash meeting on Saturday to do planning/proj management stuff
- Eric doing image processing research instead of login stuff