from fastapi import APIRouter, HTTPException, status

from schemas.course_schema import AccessCodeResponse, CourseCreate, CourseResponse, EnrollRequest
from core.dependencies import CourseServiceDep, RequiredUserDep
from services.course_service import (
    AlreadyEnrolledError,
    CourseNotFoundError,
    EnrolledCourse,
    NotAllowedToCreateCourseError,
    NotCourseInstructorError,
)

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


@router.get("", response_model=list[CourseResponse])
def get_my_courses(course_service: CourseServiceDep, current_user: RequiredUserDep):
    """List every course the logged-in user is enrolled in, newest enrollment first."""
    return [_to_response(enrolled) for enrolled in course_service.get_courses_for_user(current_user)]


@router.post("/enroll", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
def enroll(body: EnrollRequest, course_service: CourseServiceDep, current_user: RequiredUserDep):
    """Enroll the logged-in user as a student in the course with the given access code."""
    try:
        enrolled = course_service.enroll(body.access_code, current_user)
    except CourseNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except AlreadyEnrolledError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    return _to_response(enrolled)


@router.get("/{course_id}/access-code", response_model=AccessCodeResponse)
def get_access_code(course_id: int, course_service: CourseServiceDep, current_user: RequiredUserDep):
    """Return the course's access code. Only instructors of the course and admins can see it."""
    try:
        access_code = course_service.get_access_code(course_id, current_user)
    except CourseNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except NotCourseInstructorError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc
    return AccessCodeResponse(access_code=access_code)
