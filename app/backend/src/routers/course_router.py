from fastapi import APIRouter, HTTPException, status

from schemas.course_schema import CourseCreate, CourseResponse
from core.dependencies import CourseServiceDep, RequiredUserDep
from services.course_service import EnrolledCourse, NotAllowedToCreateCourseError

router = APIRouter(prefix="/courses", tags=["courses"])


def _to_response(enrolled: EnrolledCourse) -> CourseResponse:
    """Build the response, including the access code only for instructors of the course."""
    course = enrolled.course
    return CourseResponse(
        id=course.id,
        name=course.name,
        language_id=course.language_id,
        owner_id=course.owner_id,
        is_instructor=enrolled.is_instructor,
        access_code=course.access_code if enrolled.is_instructor else None,
        created_at=course.created_at,
    )


@router.post("", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
def create_course(body: CourseCreate, course_service: CourseServiceDep, current_user: RequiredUserDep):
    """Create a course owned by the logged-in instructor and enroll them as its instructor."""
    try:
        course = course_service.create_course(body, current_user)
    except NotAllowedToCreateCourseError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc
    return _to_response(EnrolledCourse(course, is_instructor=True))
