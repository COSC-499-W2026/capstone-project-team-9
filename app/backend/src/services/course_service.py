"""Create courses and generate their access codes."""
import secrets
from dataclasses import dataclass

from models import Course, User
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
