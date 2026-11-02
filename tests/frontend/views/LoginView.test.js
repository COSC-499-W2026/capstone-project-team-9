import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import LoginView from '../../../src/views/LoginView.vue'
import { post } from '../../../src/api/client.js'

vi.mock('../../../src/api/client.js', () => ({
  post: vi.fn(),
}))

describe('LoginView', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('displays the login form', () => {
    const wrapper = mount(LoginView)

    expect(wrapper.find('h2').text()).toBe('Login')
    expect(wrapper.find('input[type="email"]').exists()).toBe(true)
    expect(wrapper.find('input[type="password"]').exists()).toBe(true)
    expect(wrapper.find('button[type="submit"]').text()).toBe('Login')
  })

  it('submits the email and password', async () => {
    post.mockResolvedValue({ name: 'Alice' })

    const wrapper = mount(LoginView)

    await wrapper.find('input[type="email"]').setValue('alice@example.com')
    await wrapper.find('input[type="password"]').setValue('StrongPass123!')
    await wrapper.find('form').trigger('submit')
    await flushPromises()

    expect(post).toHaveBeenCalledWith('/login', {
      email: 'alice@example.com',
      password: 'StrongPass123!',
    })
  })

  it('displays a welcome message after successful login', async () => {
    post.mockResolvedValue({ name: 'Alice' })

    const wrapper = mount(LoginView)

    await wrapper.find('input[type="email"]').setValue('alice@example.com')
    await wrapper.find('input[type="password"]').setValue('StrongPass123!')
    await wrapper.find('form').trigger('submit')
    await flushPromises()

    expect(wrapper.text()).toContain('Welcome, Alice!')
  })

  it('displays an error message when login fails', async () => {
    post.mockRejectedValue(new Error('Request failed (401)'))

    const wrapper = mount(LoginView)

    await wrapper.find('input[type="email"]').setValue('alice@example.com')
    await wrapper.find('input[type="password"]').setValue('wrong')
    await wrapper.find('form').trigger('submit')
    await flushPromises()

    expect(wrapper.text()).toContain(
      'Login failed. Check your email and password.',
    )
  })
})