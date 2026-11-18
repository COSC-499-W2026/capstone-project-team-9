from datetime import datetime, timedelta, timezone

import pytest

from models import Course, Enrollment
from repositories import EnrollmentRepository

USER_ID = 1
OTHER_USER_ID = 2


@pytest.fixture
def enrollment_repo(session):
    return EnrollmentRepository(session)


@pytest.fixture
def add_course(session):
    """Factory: add_course(name) saves a course and returns it."""
    def _add(name: str = "Spanish 101") -> Course:
        course = Course(name=name, language_id=1)
        session.add(course)
        session.commit()
        session.refresh(course)
        return course
    return _add


def test_add_enrollment_saves_and_returns_it(session, enrollment_repo, add_course):
    course = add_course()
    enrollment = enrollment_repo.add_enrollment(Enrollment(user_id=USER_ID, course_id=course.id))
    assert (enrollment.user_id, enrollment.course_id) == (USER_ID, course.id)
    assert enrollment.is_instructor is False
    assert session.get(Enrollment, (USER_ID, course.id)) is not None


def test_get_enrollment_found_and_missing(enrollment_repo, add_course):
    course = add_course()
    enrollment_repo.add_enrollment(Enrollment(user_id=USER_ID, course_id=course.id))
    assert enrollment_repo.get_enrollment(USER_ID, course.id) is not None
    assert enrollment_repo.get_enrollment(OTHER_USER_ID, course.id) is None
    assert enrollment_repo.get_enrollment(USER_ID, 999) is None


def test_get_courses_for_user_returns_courses_with_instructor_flag_newest_first(enrollment_repo, add_course):
    older, newer = add_course("Older"), add_course("Newer")
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    enrollment_repo.add_enrollment(
        Enrollment(user_id=USER_ID, course_id=older.id, is_instructor=True, created_at=start)
    )
    enrollment_repo.add_enrollment(
        Enrollment(user_id=USER_ID, course_id=newer.id, created_at=start + timedelta(days=1))
    )

    result = enrollment_repo.get_courses_for_user(USER_ID)

    assert [(course.id, is_instructor) for course, is_instructor in result] == [
        (newer.id, False),
        (older.id, True),
    ]


def test_get_courses_for_user_excludes_other_users_courses(enrollment_repo, add_course):
    course = add_course()
    enrollment_repo.add_enrollment(Enrollment(user_id=OTHER_USER_ID, course_id=course.id))
    assert enrollment_repo.get_courses_for_user(USER_ID) == []
