import pytest
from sqlmodel import select

from models import Course, Enrollment, Language, User
from models.user_model import UserRole
from schemas.course_schema import CourseCreate
from services.course_service import (
    ACCESS_CODE_ALPHABET,
    ACCESS_CODE_LENGTH,
    MAX_CODE_ATTEMPTS,
    CourseService,
    NotAllowedToCreateCourseError,
)
from repositories import CourseRepository, GameOptionsRepository   # TODO in future: MOCK these repositories


@pytest.fixture
def seeded(session):
    session.add(Language(name="Spanish"))
    session.commit()


@pytest.fixture
def make_user(session):
    """Factory: make_user(role) saves a user with that role and returns it."""
    def _make(role: str) -> User:
        user = User(name=role.title(), email=f"{role}@example.com", hashed_password="x", role=role)
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    return _make


@pytest.fixture
def instructor(make_user):
    return make_user(UserRole.INSTRUCTOR.value)


@pytest.fixture
def course_repo(session):
    return CourseRepository(session)


@pytest.fixture
def course_service(session, course_repo):
    return CourseService(course_repo, GameOptionsRepository(session))


def _settings(**overrides):
    values = {"name": "Spanish 101", "language_id": 1} | overrides
    return CourseCreate.model_construct(**values)


def _saved_courses(session):
    return session.exec(select(Course)).all()


def test_create_course_saves_owner_language_and_name(course_service, session, seeded, instructor):
    course = course_service.create_course(_settings(), instructor)
    assert course.id is not None
    assert (course.owner_id, course.language_id, course.name) == (instructor.id, 1, "Spanish 101")
    assert len(_saved_courses(session)) == 1


def test_create_course_enrolls_creator_as_instructor(course_service, session, seeded, instructor):
    course = course_service.create_course(_settings(), instructor)
    enrollment = session.get(Enrollment, (instructor.id, course.id))
    assert enrollment is not None
    assert enrollment.is_instructor is True


def test_access_code_has_the_right_length_and_alphabet(course_service, seeded, instructor):
    code = course_service.create_course(_settings(), instructor).access_code
    assert len(code) == ACCESS_CODE_LENGTH
    assert set(code) <= set(ACCESS_CODE_ALPHABET)


def test_each_course_gets_a_different_access_code(course_service, seeded, instructor):
    codes = {course_service.create_course(_settings(), instructor).access_code for _ in range(20)}
    assert len(codes) == 20


def test_create_course_trims_the_name(course_service, seeded, instructor):
    assert course_service.create_course(_settings(name="  Spanish 101  "), instructor).name == "Spanish 101"


def test_admin_can_create_a_course(course_service, seeded, make_user):
    admin = make_user(UserRole.ADMIN.value)
    assert course_service.create_course(_settings(), admin).owner_id == admin.id


def test_student_cannot_create_a_course_and_nothing_is_saved(course_service, session, seeded, make_user):
    student = make_user(UserRole.STUDENT.value)
    with pytest.raises(NotAllowedToCreateCourseError):
        course_service.create_course(_settings(), student)
    assert _saved_courses(session) == []


def test_unknown_language_is_rejected_and_nothing_is_saved(course_service, session, seeded, instructor):
    with pytest.raises(ValueError, match="Language does not exist"):
        course_service.create_course(_settings(language_id=999), instructor)
    assert _saved_courses(session) == []


def test_access_code_generation_retries_on_collision(course_service, course_repo, mocker):
    exists = mocker.patch.object(course_repo, "access_code_exists", side_effect=[True, True, False])
    course_service._generate_access_code()
    assert exists.call_count == 3


def test_access_code_generation_gives_up_if_every_code_is_taken(course_service, course_repo, mocker):
    exists = mocker.patch.object(course_repo, "access_code_exists", return_value=True)
    with pytest.raises(RuntimeError):
        course_service._generate_access_code()
    assert exists.call_count == MAX_CODE_ATTEMPTS
