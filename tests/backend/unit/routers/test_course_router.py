import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlmodel import select

from core.db import get_session
from core.dependencies import get_current_user
from models import Course, Enrollment, Language, User
from models.user_model import UserRole
from routers.course_router import router
from services.course_service import ACCESS_CODE_LENGTH


@pytest.fixture
def app(session):
    session.add(Language(name="Spanish"))
    session.commit()
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_session] = lambda: session
    return app


@pytest.fixture
def client_as(app):
    """Factory: client_as(user) returns a client logged in as that user. None means a bad token."""
    def _client(user: User | None) -> TestClient:
        app.dependency_overrides[get_current_user] = lambda: user
        return TestClient(app, headers={"Authorization": "Bearer test"})
    return _client


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
def teacher(make_user):
    return make_user(UserRole.INSTRUCTOR.value)


def _body(**overrides):
    return {"name": "Spanish 101", "language_id": 1} | overrides


def _saved_courses(session):
    return session.exec(select(Course)).all()


def test_create_course_returns_201_with_access_code(client_as, teacher):
    r = client_as(teacher).post("/courses", json=_body())
    assert r.status_code == 201
    data = r.json()
    assert len(data["access_code"]) == ACCESS_CODE_LENGTH
    assert data["is_instructor"] is True
    assert (data["name"], data["language_id"], data["owner_id"]) == ("Spanish 101", 1, teacher.id)


def test_create_course_enrolls_the_teacher(client_as, session, teacher):
    course_id = client_as(teacher).post("/courses", json=_body()).json()["id"]
    enrollment = session.get(Enrollment, (teacher.id, course_id))
    assert enrollment is not None
    assert enrollment.is_instructor is True


def test_student_gets_403_and_nothing_is_saved(client_as, session, make_user):
    student = make_user(UserRole.STUDENT.value)
    assert client_as(student).post("/courses", json=_body()).status_code == 403
    assert _saved_courses(session) == []


def test_unknown_language_returns_422(client_as, teacher):
    r = client_as(teacher).post("/courses", json=_body(language_id=999))
    assert r.status_code == 422
    assert r.json()["detail"] == "Language does not exist"


@pytest.mark.parametrize("name", ["", "   ", "x" * 101])
def test_invalid_name_returns_422(client_as, session, teacher, name):
    assert client_as(teacher).post("/courses", json=_body(name=name)).status_code == 422
    assert _saved_courses(session) == []


def test_bad_token_returns_401(client_as):
    assert client_as(None).post("/courses", json=_body()).status_code == 401


def test_missing_authorization_header_returns_401(app):
    assert TestClient(app).post("/courses", json=_body()).status_code == 401


# ENROLLMENT -----------------------------------------------------------------

@pytest.fixture
def student(make_user):
    return make_user(UserRole.STUDENT.value)


@pytest.fixture
def course(client_as, teacher):
    """A course created by the teacher; returns the response JSON (includes access_code)."""
    return client_as(teacher).post("/courses", json=_body()).json()


def test_enroll_returns_201_and_hides_access_code(client_as, session, student, course):
    r = client_as(student).post("/courses/enroll", json={"access_code": course["access_code"]})
    assert r.status_code == 201
    data = r.json()
    assert data["id"] == course["id"]
    assert data["is_instructor"] is False
    assert data["access_code"] is None
    enrollment = session.get(Enrollment, (student.id, course["id"]))
    assert enrollment is not None and enrollment.is_instructor is False


def test_enroll_accepts_lowercase_code_with_spaces(client_as, student, course):
    code = f"  {course['access_code'].lower()} "
    assert client_as(student).post("/courses/enroll", json={"access_code": code}).status_code == 201


def test_enroll_unknown_code_returns_404(client_as, student, course):
    r = client_as(student).post("/courses/enroll", json={"access_code": "ZZZZZZ"})
    assert r.status_code == 404


def test_enroll_twice_returns_409(client_as, student, course):
    client = client_as(student)
    client.post("/courses/enroll", json={"access_code": course["access_code"]})
    r = client.post("/courses/enroll", json={"access_code": course["access_code"]})
    assert r.status_code == 409


def test_enroll_as_course_instructor_returns_409(client_as, teacher, course):
    r = client_as(teacher).post("/courses/enroll", json={"access_code": course["access_code"]})
    assert r.status_code == 409


@pytest.mark.parametrize("code", ["", "ABC", "ABCDEFG"])
def test_enroll_wrong_length_code_returns_422(client_as, student, code):
    assert client_as(student).post("/courses/enroll", json={"access_code": code}).status_code == 422


def test_enroll_bad_token_returns_401(client_as):
    assert client_as(None).post("/courses/enroll", json={"access_code": "ABCDEF"}).status_code == 401


# MY COURSES -----------------------------------------------------------------

def test_get_courses_returns_empty_list_for_new_user(client_as, student):
    r = client_as(student).get("/courses")
    assert r.status_code == 200
    assert r.json() == []


def test_get_courses_shows_access_code_only_to_instructor(client_as, teacher, student, course):
    client_as(student).post("/courses/enroll", json={"access_code": course["access_code"]})

    [teacher_view] = client_as(teacher).get("/courses").json()
    [student_view] = client_as(student).get("/courses").json()

    assert teacher_view["is_instructor"] is True
    assert teacher_view["access_code"] == course["access_code"]
    assert student_view["is_instructor"] is False
    assert student_view["access_code"] is None


def test_get_courses_bad_token_returns_401(client_as):
    assert client_as(None).get("/courses").status_code == 401


# ACCESS CODE ----------------------------------------------------------------

def test_instructor_gets_access_code(client_as, teacher, course):
    r = client_as(teacher).get(f"/courses/{course['id']}/access-code")
    assert r.status_code == 200
    assert r.json() == {"access_code": course["access_code"]}


def test_admin_gets_access_code_without_enrollment(client_as, make_user, course):
    admin = make_user(UserRole.ADMIN.value)
    r = client_as(admin).get(f"/courses/{course['id']}/access-code")
    assert r.status_code == 200
    assert r.json() == {"access_code": course["access_code"]}


def test_enrolled_student_gets_403_for_access_code(client_as, student, course):
    client_as(student).post("/courses/enroll", json={"access_code": course["access_code"]})
    assert client_as(student).get(f"/courses/{course['id']}/access-code").status_code == 403


def test_access_code_for_unknown_course_returns_404(client_as, teacher):
    assert client_as(teacher).get("/courses/999/access-code").status_code == 404


def test_access_code_bad_token_returns_401(client_as, course):
    assert client_as(None).get(f"/courses/{course['id']}/access-code").status_code == 401
