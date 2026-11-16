import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'

const push = vi.fn()
vi.mock('vue-router', () => ({ useRouter: () => ({ push }) }))
vi.mock('../../../src/api/login.js', () => ({ requestToken: vi.fn() }))
vi.mock('../../../src/utils/auth.js', () => ({ setToken: vi.fn() }))

import LoginView from '../../../src/views/LoginView.vue'
import { requestToken } from '../../../src/api/login.js'
import { setToken } from '../../../src/utils/auth.js'

async function submit(wrapper, password) {
  await wrapper.find('input[type="email"]').setValue('alice@example.com')
  await wrapper.find('input[type="password"]').setValue(password)
  await wrapper.find('form').trigger('submit')
  await flushPromises()
}

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

  it('requests a token with the email and password', async () => {
    requestToken.mockResolvedValue({ access_token: 'tok' })

    await submit(mount(LoginView), 'StrongPass123!')

    expect(requestToken).toHaveBeenCalledWith('alice@example.com', 'StrongPass123!')
  })

  it('stores the token and goes to the play screen on success', async () => {
    requestToken.mockResolvedValue({ access_token: 'tok' })

    await submit(mount(LoginView), 'StrongPass123!')

    expect(setToken).toHaveBeenCalledWith('tok')
    expect(push).toHaveBeenCalledWith({ name: 'play' })
  })

  it('shows an error and stores nothing when login fails', async () => {
    requestToken.mockRejectedValue(new Error('Request failed (401)'))

    const wrapper = mount(LoginView)
    await submit(wrapper, 'wrong')

    expect(wrapper.text()).toContain('Login failed. Check your email and password.')
    expect(setToken).not.toHaveBeenCalled()
    expect(push).not.toHaveBeenCalled()
  })
})