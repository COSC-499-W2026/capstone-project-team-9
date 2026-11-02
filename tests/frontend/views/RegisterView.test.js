import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import RegisterView from '@/src/views/RegisterView.vue'
import { post } from '@/src/api/client.js'

vi.mock('@/src/api/client.js', () => ({
  post: vi.fn(),
}))

describe('RegisterView', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('displays the registration form', () => {
    const wrapper = mount(RegisterView)

    expect(wrapper.find('h2').text()).toBe('Register')
    expect(wrapper.find('input#name').exists()).toBe(true)
    expect(wrapper.find('input[type="email"]').exists()).toBe(true)
    expect(wrapper.find('input[type="password"]').exists()).toBe(true)
    expect(wrapper.find('button[type="submit"]').text()).toBe('Register')
  })

  it('submits the registration details', async () => {
    post.mockResolvedValue({
      name: 'Alice',
      email: 'alice@example.com',
    })

    const wrapper = mount(RegisterView)

    await wrapper.find('#name').setValue('Alice')
    await wrapper.find('#email').setValue('alice@example.com')
    await wrapper.find('#password').setValue('StrongPass123!')
    await wrapper.find('form').trigger('submit')

    await flushPromises()

    expect(post).toHaveBeenCalledWith('/users/register', {
      name: 'Alice',
      email: 'alice@example.com',
      password: 'StrongPass123!',
    })
  })

  it('displays a welcome message after successful registration', async () => {
    post.mockResolvedValue({
      name: 'Alice',
      email: 'alice@example.com',
    })

    const wrapper = mount(RegisterView)

    await wrapper.find('#name').setValue('Alice')
    await wrapper.find('#email').setValue('alice@example.com')
    await wrapper.find('#password').setValue('StrongPass123!')
    await wrapper.find('form').trigger('submit')

    await flushPromises()

    expect(wrapper.text()).toContain(
      'Registration successful! Welcome, Alice!',
    )
  })

  it('displays an error when the username or email already exists', async () => {
    post.mockRejectedValue(new Error('Request failed (409)'))

    const wrapper = mount(RegisterView)

    await wrapper.find('#name').setValue('Alice')
    await wrapper.find('#email').setValue('alice@example.com')
    await wrapper.find('#password').setValue('StrongPass123!')
    await wrapper.find('form').trigger('submit')

    await flushPromises()

    expect(wrapper.text()).toContain(
      'Username or email already exists.',
    )
  })

  it('displays an error when registration fails for another reason', async () => {
    post.mockRejectedValue(new Error('Request failed (500)'))

    const wrapper = mount(RegisterView)

    await wrapper.find('#name').setValue('Alice')
    await wrapper.find('#email').setValue('alice@example.com')
    await wrapper.find('#password').setValue('StrongPass123!')
    await wrapper.find('form').trigger('submit')

    await flushPromises()

    expect(wrapper.text()).toContain(
      'Registration failed. Please try again.',
    )
  })
})