import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'

const push = vi.fn()
vi.mock('vue-router', () => ({ useRouter: () => ({ push }) }))
vi.mock('@/api/login.js', () => ({ requestGuestToken: vi.fn() }))
vi.mock('@/utils/auth.js', () => ({ setToken: vi.fn() }))

import { requestGuestToken } from '@/api/login.js'
import { setToken } from '@/utils/auth.js'
import LandingView from '@/views/LandingView.vue'

const mountLanding = () =>
  mount(LandingView, { global: { stubs: { RouterLink: { props: ['to'], template: '<a :href="to"><slot /></a>' } } } })

beforeEach(() => vi.clearAllMocks())

describe('LandingView', () => {
  it('offers log in, register and play as guest', () => {
    const wrapper = mountLanding()

    expect(wrapper.find('a[href="/login"]').exists()).toBe(true)
    expect(wrapper.find('a[href="/register"]').exists()).toBe(true)
    expect(wrapper.find('button').text()).toBe('Play as guest')
  })

  it('stores a guest token and goes to the play screen', async () => {
    requestGuestToken.mockResolvedValue({ access_token: 'guest-tok' })
    const wrapper = mountLanding()

    await wrapper.find('button').trigger('click')
    await flushPromises()

    expect(setToken).toHaveBeenCalledWith('guest-tok')
    expect(push).toHaveBeenCalledWith({ name: 'play' })
  })

  it('shows an error and stores nothing when the guest request fails', async () => {
    requestGuestToken.mockRejectedValue(new Error('Request failed (500)'))
    const wrapper = mountLanding()

    await wrapper.find('button').trigger('click')
    await flushPromises()

    expect(wrapper.text()).toContain("Couldn't start a guest session")
    expect(setToken).not.toHaveBeenCalled()
    expect(push).not.toHaveBeenCalled()
  })
})