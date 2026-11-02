# Individual Log - Week 8
_Ian Steyn_

## For PR [#161 Cleanup db and test folders](https://github.com/COSC-499-W2026/capstone-project-team-9/pull/161)

> Mini-PR: template does not apply

Just some helpful file organization cleanup:
- grouped backend tests into folders that mirror the structure of the backend
  - e.g. all repo tests go in `test_repos/`
- Got rid of the `db/` folder and moved its contents into `docs/` and `tests/`
  - we no longer needed a dedicated db folder outside of `app/` and it was cluttering up our root

---

## For PR [#162 Combine coverage report with main CI workflow](https://github.com/COSC-499-W2026/capstone-project-team-9/pull/162)

> Mini-PR: template does not apply

> Associated issues: [#136 Combine coverage and main tests into a single workflow](https://github.com/COSC-499-W2026/capstone-project-team-9/issues/136)

Our backend tests were running twice for every push to a PR branch or `main`, which made our CI take longer than neccessary and cluttered up our checks logs. Therefore I:
- deleted `cov.yaml`
- moved coverage stuff into the "Backend Tests" job of `ci.yaml` so that backend tests only have to run once

---

## For PR [#207 Improve location modelling + seed target data with locations](https://github.com/COSC-499-W2026/capstone-project-team-9/pull/207):

> associated issues:
> - [#172 seed location data](https://github.com/COSC-499-W2026/capstone-project-team-9/issues/172)

### What I did

As part of the requirement to check a user's location when they start a game or submit an answer, the user needs to be able to pass a latitude and longitude to the backend, and have that point check against an allowed area.

We already have services that do this, our modelling for this was unclear and tangled. Therefore, I implemented the following code:
- Added new base models called `LocationPoint` and `LocationArea`
- `LocationCheckRequest` schema now inherits from `LocationPoint` instead of `BaseModel`
- `Target` model now inherits from `LocationArea` instead of `SQLModel` and no longer has an `image` field
- Removed `TargetLocation` dataclass from `location_service.py`

I also added seed data for locations to our seeding scripts, so we can test location-related stuff with our development database.

### Verification and Problem-solving

When I reviewed the [reference specific part(s) of generated code] for this functionality, I did not find any problems with it because [explain verification approach taken].  
OR  
When I reviewed the tests for models, I noticed that `test_model_registration` failed, but this didn't really make sense because `location_model.py` contains no tables that need to be registered. Therefore, I did made an official list of `EXEMPT_FILES` which no includes `__init__.py` and `location_model`.  


### Engineering Practices

The PR does not contain any temporary workaround because:
- I used real UBCO building coordinates for seeding data
- I properly documented all new models and modules using docstrings
- I removed a previous model that was erroneously defined inside a service class

The PR contains no new functions, only new data models.

I did the following:
- made location data models with identical fields inherit from shared base classes

... to ensure that my feature contribution does not contain any of the following:
```
 - hardcoded values
 - duplicate code
 - dead code
 - unnecessary function calls
 - excessive conditional logic
 - deep nesting
 - high cyclomatic complexity
 - classes/modules/functions with many unrelated responsibilities
 ```

### Reviews

The reviews by Joe and Eric identified no problems.

### Architecture Impacts

The new location base models are written in `models/location_model.py` because they are data definition objects that are extended by the `Target` model as well as some schemas.

This work belongs in [existing/new process name] in the DFD because [architectural design reason].

### Data Receipts

`LocationPoint` is modeled as a pair of floating point numbers `latitude` and `longitude` because it represents a simple geographic location. We considered alternative models such as using a specialized data type like a `geoalchemy2` `Geography` point - however we are not dealing with large distances, and we want to test whether simple floating point is precise enough for the use-case, so that we don't need to add yet another dependency. If not, we'll switch.

`Latitude` and `longitude` use validation to ensure they are within real-world latitude and longitude values. `radius` uses validation to ensure it is a possible real-world radius, i.e. larger than 0. 


### Testing Receipts?

---

## For PR [#217 Base Repository Class](https://github.com/COSC-499-W2026/capstone-project-team-9/pull/217)

### What I did

In anticipation of refactoring our backend to use cleaner dependency injection (see #214 below), I implemented a base class for repositories called `BaseRepository`, which takes a database `session` in its constructor.

### Verification and Problem-solving

When I reviewed the [reference specific part(s) of generated code] for this functionality, I did not find any problems with it because [explain verification approach taken].  
OR  
When I reviewed the [reference specific part(s) of generated code] for this functionality, I noticed [identify problem details and why it is problematic]. Therefore, I did [explain solution taken].  
(Repeat for additional problems found.)

### Engineering Practices

The PR does not contain any temporary workaround because:
- TODO small enough to be very simple, makes progress towards refactor without breaking or modifying any existing structures

The PR only contains small functions that are 1 line long.

I did the following:
- defined a base repository class so that I won't have to repeat the same constructor across all repos

...to ensure that my feature contribution does not contain any of the following:
```
 - hardcoded values
 - duplicate code
 - dead code
 - unnecessary function calls
 - excessive conditional logic
 - deep nesting
 - high cyclomatic complexity
 - classes/modules/functions with many unrelated responsibilities
 ```

### Reviews

The reviews by Eric and Nash identified no problems.

### Architecture Impacts

This work is written in `repositories/base_repository.py` because that is where all repositories go, as a part of our layered architecture design.

This work does not belong in a DFD, as it defines a base class for actual repositories.

### Testing Receipts?

---

## For PR [#214 Dependency Injection Improvements](https://github.com/COSC-499-W2026/capstone-project-team-9/pull/214)

---

## For PR [#226 hotfix: fix broken tests with Play service Class conversion](https://github.com/COSC-499-W2026/capstone-project-team-9/pull/226)

---

## Other stuff

- finally finished issue [#46 Move Requirements in Project Board](https://github.com/COSC-499-W2026/capstone-project-team-9/issues/46)
- reviewed PRs: [#210](https://github.com/COSC-499-W2026/capstone-project-team-9/pull/210), [#213](https://github.com/COSC-499-W2026/capstone-project-team-9/pull/213), [#216](https://github.com/COSC-499-W2026/capstone-project-team-9/pull/216), [#215](https://github.com/COSC-499-W2026/capstone-project-team-9/pull/215), [#221](https://github.com/COSC-499-W2026/capstone-project-team-9/pull/221), [#222](https://github.com/COSC-499-W2026/capstone-project-team-9/pull/222), [#223](https://github.com/COSC-499-W2026/capstone-project-team-9/pull/223)

