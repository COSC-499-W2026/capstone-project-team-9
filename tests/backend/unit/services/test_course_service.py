import pytest
from sqlmodel import select

from models import Course, Enrollment, Language, User
from models.user_model import UserRole
from schemas.course_schema import CourseCreate
from services.course_service import (
    ACCESS_CODE_ALPHABET,
    ACCESS_CODE_LENGTH,
    MAX_CODE_ATTEMPTS,
    AlreadyEnrolledError,
    CourseNotFoundError,
    CourseService,
    NotAllowedToCreateCourseError,
    NotCourseInstructorError,
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


@pytest.fixture
def student(make_user):
    return make_user(UserRole.STUDENT.value)


@pytest.fixture
def course(course_service, seeded, instructor):
    return course_service.create_course(_settings(), instructor)


def test_enroll_adds_the_user_as_a_student(course_service, session, course, student):
    enrolled = course_service.enroll(course.access_code, student)
    assert enrolled.course.id == course.id
    assert enrolled.is_instructor is False
    enrollment = session.get(Enrollment, (student.id, course.id))
    assert enrollment is not None
    assert enrollment.is_instructor is False


def test_enroll_accepts_lowercase_and_padded_codes(course_service, course, student):
    enrolled = course_service.enroll(f"  {course.access_code.lower()}  ", student)
    assert enrolled.course.id == course.id


def test_enroll_with_unknown_code_raises_and_saves_nothing(course_service, session, course, student):
    with pytest.raises(CourseNotFoundError):
        course_service.enroll("ZZZZZZ", student)
    assert session.get(Enrollment, (student.id, course.id)) is None


def test_enrolling_twice_raises_and_keeps_a_single_enrollment(course_service, session, course, student):
    course_service.enroll(course.access_code, student)
    with pytest.raises(AlreadyEnrolledError):
        course_service.enroll(course.access_code, student)
    enrollments = session.exec(select(Enrollment).where(Enrollment.user_id == student.id)).all()
    assert len(enrollments) == 1


def test_instructor_enrolling_in_own_course_raises_and_stays_instructor(course_service, session, course, instructor):
    with pytest.raises(AlreadyEnrolledError):
        course_service.enroll(course.access_code, instructor)
    assert session.get(Enrollment, (instructor.id, course.id)).is_instructor is True


def test_get_courses_for_user_lists_enrolled_courses_with_role(course_service, course, student, instructor):
    course_service.enroll(course.access_code, student)
    student_courses = course_service.get_courses_for_user(student)
    instructor_courses = course_service.get_courses_for_user(instructor)
    assert [(c.course.id, c.is_instructor) for c in student_courses] == [(course.id, False)]
    assert [(c.course.id, c.is_instructor) for c in instructor_courses] == [(course.id, True)]


def test_get_courses_for_user_is_empty_when_not_enrolled(course_service, course, student):
    assert course_service.get_courses_for_user(student) == []


def test_instructor_can_get_the_access_code(course_service, course, instructor):
    assert course_service.get_access_code(course.id, instructor) == course.access_code


def test_admin_can_get_the_access_code_without_being_enrolled(course_service, course, make_user):
    admin = make_user(UserRole.ADMIN.value)
    assert course_service.get_access_code(course.id, admin) == course.access_code


def test_enrolled_student_cannot_get_the_access_code(course_service, course, student):
    course_service.enroll(course.access_code, student)
    with pytest.raises(NotCourseInstructorError):
        course_service.get_access_code(course.id, student)


def test_instructor_of_another_course_cannot_get_the_access_code(course_service, session, course):
    other_instructor = User(
        name="Other", email="other@example.com", hashed_password="x", role=UserRole.INSTRUCTOR.value
    )
    session.add(other_instructor)
    session.commit()
    with pytest.raises(NotCourseInstructorError):
        course_service.get_access_code(course.id, other_instructor)


def test_get_access_code_for_unknown_course_raises(course_service, course, instructor):
    with pytest.raises(CourseNotFoundError):
        course_service.get_access_code(999, instructor)
