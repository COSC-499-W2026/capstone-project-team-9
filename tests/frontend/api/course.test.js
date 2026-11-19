import { beforeEach, describe, expect, it, vi } from 'vitest'

vi.mock('@/api/client', () => ({
  get: vi.fn().mockResolvedValue({}),
  post: vi.fn().mockResolvedValue({}),
}))

import { get, post } from '@/api/client'
import {
  createCourse,
  enrollInCourse,
  getAccessCode,
  getMyCourse,
  getMyCourses,
} from '@/api/course'

beforeEach(() => vi.clearAllMocks())

describe('course api', () => {

  it('getMyCourses() gets the user courses', async () => {
    await getMyCourses()

    expect(get).toHaveBeenCalledWith('/courses')
  })

  it('createCourse() posts the settings in the backend field names', async () => {
    await createCourse({ name: 'French 101', languageId: 2 })

    expect(post).toHaveBeenCalledWith('/courses', { name: 'French 101', language_id: 2 })
  })

  it('enrollInCourse() posts the access code', async () => {
    await enrollInCourse('ABC234')

    expect(post).toHaveBeenCalledWith('/courses/enroll', { access_code: 'ABC234' })
  })

  it('getAccessCode() gets the course access code', async () => {
    await getAccessCode(5)

    expect(get).toHaveBeenCalledWith('/courses/5/access-code')
  })

  it('getMyCourse() finds the course by id, even when the id is a route string', async () => {
    get.mockResolvedValueOnce([{ id: 1 }, { id: 5, name: 'French' }])

    expect(await getMyCourse('5')).toEqual({ id: 5, name: 'French' })
  })

  it('getMyCourse() resolves null when the user is not in the course', async () => {
    get.mockResolvedValueOnce([{ id: 1 }])

    expect(await getMyCourse(9)).toBeNull()
  })
})
