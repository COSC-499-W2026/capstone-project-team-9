import { beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'

vi.mock('@/api/client', () => ({ get: vi.fn() }))

import { get } from '@/api/client'
import ClueAudioPlaceholder from '@/components/ClueAudioPlaceholder.vue'

async function mountLoaded() {
  const wrapper = mount(ClueAudioPlaceholder, { props: { clueId: 11 } })
  await flushPromises()
  return wrapper
}

beforeEach(() => vi.resetAllMocks())

describe('ClueAudioPlaceholder', () => {
  it('says clue audio is coming soon', async () => {
    get.mockRejectedValue(new Error('Request failed (404)'))
    const wrapper = await mountLoaded()

    expect(wrapper.text()).toContain('Clue audio coming soon')
  })

  it('shows the clue room for testing in development', async () => {
    get.mockResolvedValue({ room: 'COM 312' })
    const wrapper = await mountLoaded()

    expect(get).toHaveBeenCalledWith('/dev/clues/11/room')
    expect(wrapper.text()).toContain('Test mode · Room COM 312')
  })

  it('shows no room outside development', async () => {
    get.mockRejectedValue(new Error('Request failed (404)'))
    const wrapper = await mountLoaded()

    expect(wrapper.text()).not.toContain('Test mode')
  })
})
