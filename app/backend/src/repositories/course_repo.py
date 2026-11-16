from sqlmodel import select

from repositories import BaseRepository
from models import Course, Enrollment


class CourseRepository(BaseRepository):
    """
    Repository class for interacting with Course data
    """

    def add_course_with_owner(self, course: Course) -> Course:
        """
        Save a new course and enroll its owner as the instructor in one commit.
        course.owner_id must be set.
        """
        self.session.add(course)
        self.session.flush()  # assigns course.id
        self.session.add(
            Enrollment(user_id=course.owner_id, course_id=course.id, is_instructor=True)
        )
        self.session.commit()
        self.session.refresh(course)
        return course


    def get_course(self, course_id: int) -> Course | None:
        return self.session.get(Course, course_id)


    def get_by_access_code(self, access_code: str) -> Course | None:
        statement = select(Course).where(Course.access_code == access_code)
        return self.session.exec(statement).first()


    def access_code_exists(self, access_code: str) -> bool:
        statement = select(Course.id).where(Course.access_code == access_code).limit(1)
        return self.session.exec(statement).first() is not None
