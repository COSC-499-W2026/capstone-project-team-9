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


    def add_enrollment(self, enrollment: Enrollment) -> Enrollment:
        self.session.add(enrollment)
        self.session.commit()
        self.session.refresh(enrollment)
        return enrollment


    def get_enrollment(self, user_id: int, course_id: int) -> Enrollment | None:
        return self.session.get(Enrollment, (user_id, course_id))


    def get_courses_for_user(self, user_id: int) -> list[tuple[Course, bool]]:
        """
        Return every course the user is enrolled in, paired with whether
        they are an instructor of that course. Newest enrollment first.
        """
        statement = (
            select(Course, Enrollment.is_instructor)
            .join(Enrollment, Enrollment.course_id == Course.id)
            .where(Enrollment.user_id == user_id)
            .order_by(Enrollment.created_at.desc())
        )
        return list(self.session.exec(statement).all())
