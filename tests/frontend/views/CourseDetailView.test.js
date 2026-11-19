import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises, RouterLinkStub } from '@vue/test-utils'

const push = vi.fn()
vi.mock('vue-router', () => ({ useRouter: () => ({ push }) }))
vi.mock('../../../src/api/course.js', () => ({
  getMyCourse: vi.fn(),
  getAccessCode: vi.fn(),
}))
vi.mock('../../../src/api/game.js', () => ({ getLanguages: vi.fn() }))

import CourseDetailView from '../../../src/views/CourseDetailView.vue'
import { getAccessCode, getMyCourse } from '../../../src/api/course.js'
import { getLanguages } from '../../../src/api/game.js'

async function mountWith(course) {
  getMyCourse.mockResolvedValue(course)
  getLanguages.mockResolvedValue([{ id: 1, name: 'French' }])
  const wrapper = mount(CourseDetailView, {
    props: { courseId: '10' },
    global: { stubs: { RouterLink: RouterLinkStub } },
  })
  await flushPromises()
  return wrapper
}

describe('CourseDetailView', () => {
  beforeEach(() => vi.clearAllMocks())

  it('shows the course name and language', async () => {
    const wrapper = await mountWith({ id: 10, name: 'French 101', language_id: 1, is_instructor: false })

    expect(getMyCourse).toHaveBeenCalledWith('10')
    expect(wrapper.find('h2').text()).toBe('French 101')
    expect(wrapper.text()).toContain('Language: French')
    expect(wrapper.text()).toContain('a student')
  })

  it('does not offer the access code to students', async () => {
    const wrapper = await mountWith({ id: 10, name: 'French 101', language_id: 1, is_instructor: false })

    expect(wrapper.text()).not.toContain('Get access code')
  })

  it('shows the access code to instructors when they ask for it', async () => {
    getAccessCode.mockResolvedValue({ access_code: 'ABC234' })
    const wrapper = await mountWith({ id: 10, name: 'French 101', language_id: 1, is_instructor: true })

    await wrapper.find('button').trigger('click')
    await flushPromises()

    expect(getAccessCode).toHaveBeenCalledWith(10)
    expect(wrapper.find('.access-code').text()).toContain('ABC234')
  })

  it('says so when the user is not in the course', async () => {
    const wrapper = await mountWith(null)

    expect(wrapper.text()).toContain("Course not found, or you're not enrolled in it.")
  })

  it('sends the user to login when not logged in', async () => {
    getMyCourse.mockRejectedValue(Object.assign(new Error('401'), { status: 401 }))
    getLanguages.mockResolvedValue([])

    mount(CourseDetailView, { props: { courseId: '10' }, global: { stubs: { RouterLink: RouterLinkStub } } })
    await flushPromises()

    expect(push).toHaveBeenCalledWith({ name: 'login' })
  })
})
