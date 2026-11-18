from sqlmodel import select

from repositories import BaseRepository
from models import Course, Enrollment


class EnrollmentRepository(BaseRepository):
    """
    Repository class for interacting with Enrollment data
    """

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
