import { beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'

vi.mock('@/api/location', () => ({ verifyLocation: vi.fn() }))
vi.mock('@/utils/geolocation', () => ({ getCurrentCoords: vi.fn() }))

import { verifyLocation } from '@/api/location'
import { getCurrentCoords } from '@/utils/geolocation'
import PlayView from '@/views/PlayView.vue'

async function clickPlay(wrapper) {
  await wrapper.find('button').trigger('click')
  await flushPromises()
}

beforeEach(() => {
  vi.resetAllMocks()
  getCurrentCoords.mockResolvedValue({ latitude: 49.9, longitude: -119.4 })
})

describe('PlayView', () => {
  it('shows the allowed message on campus', async () => {
    verifyLocation.mockResolvedValue({ allowed: true, message: 'Location verified.' })
    const wrapper = mount(PlayView)

    await clickPlay(wrapper)

    expect(wrapper.text()).toContain('✅')
    expect(wrapper.text()).toContain('Location verified.')
  })

  it('shows the blocked message off campus', async () => {
    verifyLocation.mockResolvedValue({ allowed: false, message: 'Head to campus!' })
    const wrapper = mount(PlayView)

    await clickPlay(wrapper)

    expect(wrapper.text()).toContain('🚫')
    expect(wrapper.text()).toContain('Head to campus!')
  })

  it('sends the device coordinates to the API', async () => {
    verifyLocation.mockResolvedValue({ allowed: true, message: 'ok' })

    await clickPlay(mount(PlayView))

    expect(verifyLocation).toHaveBeenCalledWith(49.9, -119.4)
  })

  it('shows an error when location access fails', async () => {
    getCurrentCoords.mockRejectedValue(new Error('User denied Geolocation'))
    const wrapper = mount(PlayView)

    await clickPlay(wrapper)

    expect(wrapper.text()).toContain('User denied Geolocation')
    expect(verifyLocation).not.toHaveBeenCalled()
  })

  it('shows an error when the backend call fails', async () => {
    verifyLocation.mockRejectedValue(new Error('Request failed (500)'))
    const wrapper = mount(PlayView)

    await clickPlay(wrapper)

    expect(wrapper.text()).toContain('Request failed (500)')
  })

  it('disables the button while waiting', async () => {
    verifyLocation.mockReturnValue(new Promise(() => {})) // never resolves
    const wrapper = mount(PlayView)

    await wrapper.find('button').trigger('click')

    expect(wrapper.find('button').attributes('disabled')).toBeDefined()
  })
})