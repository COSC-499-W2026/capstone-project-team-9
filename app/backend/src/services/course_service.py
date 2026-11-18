"""Create courses and generate their access codes."""
import secrets
from dataclasses import dataclass

from models import Course, Enrollment, User
from models.user_model import UserRole
from repositories import CourseRepository, GameOptionsRepository
from schemas.course_schema import CourseCreate

# No 0/O/1/I/L so codes are easy to read and type
ACCESS_CODE_ALPHABET = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"
ACCESS_CODE_LENGTH = 6
MAX_CODE_ATTEMPTS = 10
COURSE_CREATOR_ROLES = {UserRole.INSTRUCTOR.value, UserRole.ADMIN.value}


class NotAllowedToCreateCourseError(Exception):
    """Raised when a user without instructor permissions tries to create a course."""


class CourseNotFoundError(Exception):
    """Raised when no course matches the given access code or id."""


class AlreadyEnrolledError(Exception):
    """Raised when a user tries to enroll in a course they are already in."""


class NotCourseInstructorError(Exception):
    """Raised when a user who is not an instructor of the course asks for instructor-only data."""


@dataclass(frozen=True)
class EnrolledCourse:
    course: Course
    is_instructor: bool


class CourseService:
    """
    Service for validating and creating courses
    """
    def __init__(
        self,
        course_repo: CourseRepository,
        game_options_repo: GameOptionsRepository
    ):
        self.course_repo = course_repo
        self.game_options_repo = game_options_repo

    def _generate_access_code(self) -> str:
        """
        Return a random access code that no other course uses.
        Raise RuntimeError if no unused code is found after MAX_CODE_ATTEMPTS tries.
        """
        for _ in range(MAX_CODE_ATTEMPTS):
            code = "".join(secrets.choice(ACCESS_CODE_ALPHABET) for _ in range(ACCESS_CODE_LENGTH))
            if not self.course_repo.access_code_exists(code):
                return code
        raise RuntimeError(f"Could not generate a unique access code after {MAX_CODE_ATTEMPTS} attempts")


    def create_course(self, settings: CourseCreate, creator: User) -> Course:
        """
        Validate the settings and save a new course owned by the creator,
        who is enrolled in it as the instructor.
        """
        if creator.role not in COURSE_CREATOR_ROLES:
            raise NotAllowedToCreateCourseError("Only instructors can create courses")
        if self.game_options_repo.get_language(settings.language_id) is None:
            raise ValueError("Language does not exist")

        return self.course_repo.add_course_with_owner(Course(
            name=settings.name.strip(),
            language_id=settings.language_id,
            owner_id=creator.id,
            access_code=self._generate_access_code(),
        ))


    def enroll(self, access_code: str, user: User) -> EnrolledCourse:
        """
        Enroll the user as a student in the course with this access code.
        Raise CourseNotFoundError if no course uses the code,
        or AlreadyEnrolledError if the user is already in the course.
        """
        course = self.course_repo.get_by_access_code(access_code.strip().upper())
        if course is None:
            raise CourseNotFoundError("No course matches that access code")
        if self.course_repo.get_enrollment(user.id, course.id) is not None:
            raise AlreadyEnrolledError("You are already enrolled in this course")

        self.course_repo.add_enrollment(
            Enrollment(user_id=user.id, course_id=course.id, is_instructor=False)
        )
        return EnrolledCourse(course, is_instructor=False)


    def get_courses_for_user(self, user: User) -> list[EnrolledCourse]:
        """Return every course the user is enrolled in, newest enrollment first."""
        return [
            EnrolledCourse(course, is_instructor=is_instructor)
            for course, is_instructor in self.course_repo.get_courses_for_user(user.id)
        ]


    def get_access_code(self, course_id: int, user: User) -> str:
        """
        Return the course's access code so an instructor can share it with students.
        Raise CourseNotFoundError if the course does not exist,
        or NotCourseInstructorError if the user is not an instructor of the course.
        """
        course = self.course_repo.get_course(course_id)
        if course is None:
            raise CourseNotFoundError("Course does not exist")
        enrollment = self.course_repo.get_enrollment(user.id, course_id)
        if enrollment is None or not enrollment.is_instructor:
            raise NotCourseInstructorError("Only instructors of this course can view its access code")
        return course.access_code
