import pytest

from sqlmodel import select

from models import Course, Enrollment
from repositories import CourseRepository

OWNER_ID = 1
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
