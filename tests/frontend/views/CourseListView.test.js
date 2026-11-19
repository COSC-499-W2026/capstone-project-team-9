import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises, RouterLinkStub } from '@vue/test-utils'

const push = vi.fn()
vi.mock('vue-router', () => ({ useRouter: () => ({ push }) }))
vi.mock('../../../src/api/course.js', () => ({
  getCurrentUser: vi.fn(),
  getMyCourses: vi.fn(),
  createCourse: vi.fn(),
  enrollInCourse: vi.fn(),
}))
vi.mock('../../../src/api/game.js', () => ({ getLanguages: vi.fn() }))

import CourseListView from '../../../src/views/CourseListView.vue'
import { createCourse, enrollInCourse, getCurrentUser, getMyCourses } from '../../../src/api/course.js'
import { getLanguages } from '../../../src/api/game.js'

const LANGUAGES = [
  { id: 1, name: 'French' },
  { id: 2, name: 'Spanish' },
]
const COURSES = [
  { id: 10, name: 'French 101', language_id: 1, is_instructor: true },
  { id: 11, name: 'Spanish 200', language_id: 2, is_instructor: false },
]

async function mountAs(role, courses = COURSES) {
  getCurrentUser.mockResolvedValue({ name: 'U', email: 'u@example.com', role })
  getMyCourses.mockResolvedValue(courses)
  getLanguages.mockResolvedValue(LANGUAGES)
  const wrapper = mount(CourseListView, { global: { stubs: { RouterLink: RouterLinkStub } } })
  await flushPromises()
  return wrapper
}

describe('CourseListView', () => {
  beforeEach(() => vi.clearAllMocks())

  it('lists the user courses with their language', async () => {
    const wrapper = await mountAs('student')

    const items = wrapper.findAll('.course-list li')
    expect(items).toHaveLength(2)
    expect(items[0].text()).toContain('French 101')
    expect(items[0].text()).toContain('French')
    expect(items[0].text()).toContain('Instructor')
    expect(items[1].text()).toContain('Spanish 200')
    expect(wrapper.findAllComponents(RouterLinkStub)[0].props('to')).toEqual({
      name: 'course',
      params: { courseId: 10 },
    })
  })

  it('says so when the user has no courses', async () => {
    const wrapper = await mountAs('student', [])

    expect(wrapper.text()).toContain("You're not in any courses yet.")
  })

  it('sends the user to login when not logged in', async () => {
    getCurrentUser.mockRejectedValue(Object.assign(new Error('401'), { status: 401 }))
    getMyCourses.mockResolvedValue([])
    getLanguages.mockResolvedValue(LANGUAGES)

    mount(CourseListView, { global: { stubs: { RouterLink: RouterLinkStub } } })
    await flushPromises()

    expect(push).toHaveBeenCalledWith({ name: 'login' })
  })

  describe('as a teacher', () => {
    it('shows a create course button but no enroll form', async () => {
      const wrapper = await mountAs('instructor')

      expect(wrapper.find('button').text()).toBe('Create course')
      expect(wrapper.find('form.enroll').exists()).toBe(false)
    })

    it('creates a course with the typed name and chosen language, then opens it', async () => {
      createCourse.mockResolvedValue({ id: 42 })
      const wrapper = await mountAs('instructor')

      await wrapper.find('button').trigger('click')
      await wrapper.find('#course-name').setValue('  Spanish 300  ')
      await wrapper.find('#course-language').setValue(2)
      await wrapper.find('form.create-course').trigger('submit')
      await flushPromises()

      expect(createCourse).toHaveBeenCalledWith({ name: 'Spanish 300', languageId: 2 })
      expect(push).toHaveBeenCalledWith({ name: 'course', params: { courseId: 42 } })
    })

    it('lists every language in the dropdown', async () => {
      const wrapper = await mountAs('instructor')
      await wrapper.find('button').trigger('click')

      const options = wrapper.findAll('#course-language option').map((o) => o.text())
      expect(options).toEqual(['French', 'Spanish'])
    })

    it('shows the backend reason when creating fails', async () => {
      createCourse.mockRejectedValue(Object.assign(new Error('422'), { detail: 'Language does not exist' }))
      const wrapper = await mountAs('instructor')

      await wrapper.find('button').trigger('click')
      await wrapper.find('#course-name').setValue('X')
      await wrapper.find('form.create-course').trigger('submit')
      await flushPromises()

      expect(wrapper.text()).toContain('Language does not exist')
      expect(push).not.toHaveBeenCalled()
    })
  })

  describe('as a student', () => {
    it('shows the enroll form but no create course button', async () => {
      const wrapper = await mountAs('student')

      expect(wrapper.find('form.enroll').exists()).toBe(true)
      expect(wrapper.text()).not.toContain('Create course')
    })

    it('enrolls with the access code and opens the course', async () => {
      enrollInCourse.mockResolvedValue({ id: 7 })
      const wrapper = await mountAs('student')

      await wrapper.find('#access-code').setValue('abc234')
      await wrapper.find('form.enroll').trigger('submit')
      await flushPromises()

      expect(enrollInCourse).toHaveBeenCalledWith('abc234')
      expect(push).toHaveBeenCalledWith({ name: 'course', params: { courseId: 7 } })
    })

    it('shows the backend reason when enrolling fails', async () => {
      enrollInCourse.mockRejectedValue(
        Object.assign(new Error('404'), { detail: 'No course matches that access code' }),
      )
      const wrapper = await mountAs('student')

      await wrapper.find('#access-code').setValue('ZZZZZZ')
      await wrapper.find('form.enroll').trigger('submit')
      await flushPromises()

      expect(wrapper.text()).toContain('No course matches that access code')
    })
  })
})
