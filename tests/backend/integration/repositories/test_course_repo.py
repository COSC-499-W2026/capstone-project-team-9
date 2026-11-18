from datetime import datetime, timedelta, timezone

import pytest

from sqlmodel import select

from models import Course, Enrollment
from repositories import CourseRepository

OWNER_ID = 1
STUDENT_ID = 2
OTHER_USER_ID = 3
ACCESS_CODE = "ABC234"


@pytest.fixture
def course_repo(session):
    return CourseRepository(session)


def _course(**overrides):
    values = {"name": "Spanish 101", "language_id": 1, "owner_id": OWNER_ID, "access_code": ACCESS_CODE} | overrides
    return Course(**values)


def test_add_course_with_owner_saves_course_and_returns_it_with_id(session, course_repo):
    course = course_repo.add_course_with_owner(_course())
    assert course.id is not None
    assert session.get(Course, course.id) is not None


def test_add_course_with_owner_enrolls_owner_as_instructor(session, course_repo):
    course = course_repo.add_course_with_owner(_course())
    enrollments = session.exec(select(Enrollment).where(Enrollment.course_id == course.id)).all()
    assert [(e.user_id, e.is_instructor) for e in enrollments] == [(OWNER_ID, True)]


def test_get_by_access_code_found_and_missing(course_repo):
    course = course_repo.add_course_with_owner(_course())
    assert course_repo.get_by_access_code(ACCESS_CODE).id == course.id
    assert course_repo.get_by_access_code("ZZZZZZ") is None


def test_access_code_exists(course_repo):
    assert course_repo.access_code_exists(ACCESS_CODE) is False
    course_repo.add_course_with_owner(_course())
    assert course_repo.access_code_exists(ACCESS_CODE) is True
    assert course_repo.access_code_exists("ZZZZZZ") is False


def test_get_course_found_and_missing(course_repo):
    course = course_repo.add_course_with_owner(_course())
    assert course_repo.get_course(course.id).id == course.id
    assert course_repo.get_course(999) is None


def test_add_enrollment_saves_and_returns_it(session, course_repo):
    course = course_repo.add_course_with_owner(_course())
    enrollment = course_repo.add_enrollment(Enrollment(user_id=STUDENT_ID, course_id=course.id))
    assert (enrollment.user_id, enrollment.course_id) == (STUDENT_ID, course.id)
    assert enrollment.is_instructor is False
    assert session.get(Enrollment, (STUDENT_ID, course.id)) is not None


def test_get_enrollment_found_and_missing(course_repo):
    course = course_repo.add_course_with_owner(_course())
    course_repo.add_enrollment(Enrollment(user_id=STUDENT_ID, course_id=course.id))
    assert course_repo.get_enrollment(STUDENT_ID, course.id) is not None
    assert course_repo.get_enrollment(OTHER_USER_ID, course.id) is None
    assert course_repo.get_enrollment(STUDENT_ID, 999) is None


def test_get_courses_for_user_returns_courses_with_instructor_flag_newest_first(course_repo):
    older = course_repo.add_course_with_owner(_course(name="Older", access_code="AAA222"))
    newer = course_repo.add_course_with_owner(_course(name="Newer", access_code="BBB333"))
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    course_repo.add_enrollment(
        Enrollment(user_id=STUDENT_ID, course_id=older.id, is_instructor=True, created_at=start)
    )
    course_repo.add_enrollment(
        Enrollment(user_id=STUDENT_ID, course_id=newer.id, created_at=start + timedelta(days=1))
    )

    result = course_repo.get_courses_for_user(STUDENT_ID)

    assert [(course.id, is_instructor) for course, is_instructor in result] == [
        (newer.id, False),
        (older.id, True),
    ]


def test_get_courses_for_user_excludes_other_users_courses(course_repo):
    course_repo.add_course_with_owner(_course())
    assert course_repo.get_courses_for_user(STUDENT_ID) == []
