import { get, post } from './client'

/** Resolves with {name, email, role} for the logged-in user. */
export const getCurrentUser = () => get('/login/me')

/** Every course the logged-in user is in, newest enrollment first. */
export const getMyCourses = () => get('/courses')

/** Create a course owned by the logged-in instructor. */
export const createCourse = ({ name, languageId }) =>
  post('/courses', { name, language_id: languageId })

/** Join the course with this access code as a student. */
export const enrollInCourse = (accessCode) => post('/courses/enroll', { access_code: accessCode })

/** Resolves with {access_code}. Only instructors of the course (and admins) can get it. */
export const getAccessCode = (courseId) => get(`/courses/${courseId}/access-code`)

/** The course with this id, or null if the user isn't in it (there's no single-course endpoint). */
export async function getMyCourse(courseId) {
  const courses = await getMyCourses()
  return courses.find((course) => course.id === Number(courseId)) ?? null
}
