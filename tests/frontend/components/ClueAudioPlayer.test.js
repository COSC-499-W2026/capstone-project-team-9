import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'

vi.mock('@/api/client', () => ({ get: vi.fn() }))
vi.mock('@/api/clue', () => ({ fetchClueAudio: vi.fn() }))

import { get } from '@/api/client'
import { fetchClueAudio } from '@/api/clue'
import ClueAudioPlayer from '@/components/ClueAudioPlayer.vue'

const MP3 = new Blob(['mp3'], { type: 'audio/mpeg' })

let play
let pause

async function mountLoaded(clueId = 11) {
  const wrapper = mount(ClueAudioPlayer, { props: { clueId } })
  await flushPromises()
  return wrapper
}

const playButton = (wrapper) => wrapper.find('.player__button')

beforeEach(() => {
  vi.resetAllMocks()
  get.mockRejectedValue(new Error('Request failed (404)')) // not in development
  fetchClueAudio.mockResolvedValue(MP3)
  URL.createObjectURL = vi.fn(() => 'blob:audio')
  URL.revokeObjectURL = vi.fn()
  // jsdom doesn't implement media playback
  play = vi.spyOn(HTMLMediaElement.prototype, 'play').mockResolvedValue()
  pause = vi.spyOn(HTMLMediaElement.prototype, 'pause').mockImplementation(() => {})
})

afterEach(() => vi.restoreAllMocks())

describe('ClueAudioPlayer', () => {
  it('downloads the clue audio and enables the play button', async () => {
    const wrapper = await mountLoaded()

    expect(fetchClueAudio).toHaveBeenCalledWith(11)
    expect(wrapper.find('audio').attributes('src')).toBe('blob:audio')
    expect(playButton(wrapper).attributes('disabled')).toBeUndefined()
  })

  it('keeps play disabled while the audio is loading', async () => {
    fetchClueAudio.mockReturnValue(new Promise(() => {})) // never resolves
    const wrapper = await mountLoaded()

    expect(playButton(wrapper).attributes('disabled')).toBeDefined()
    expect(wrapper.text()).toContain('Loading audio')
  })

  it('plays the audio when the play button is tapped', async () => {
    const wrapper = await mountLoaded()

    await playButton(wrapper).trigger('click')

    expect(play).toHaveBeenCalledTimes(1)
  })

  it('shows a pause button while playing and pauses when tapped', async () => {
    const wrapper = await mountLoaded()
    await wrapper.find('audio').trigger('play')

    expect(playButton(wrapper).attributes('aria-label')).toBe('Pause clue')
    await playButton(wrapper).trigger('click')

    expect(pause).toHaveBeenCalledTimes(1)
  })

  it('can be replayed after it finishes', async () => {
    const wrapper = await mountLoaded()
    await playButton(wrapper).trigger('click')
    await wrapper.find('audio').trigger('play')
    await wrapper.find('audio').trigger('ended')

    expect(playButton(wrapper).attributes('aria-label')).toBe('Play clue')
    await playButton(wrapper).trigger('click')

    expect(play).toHaveBeenCalledTimes(2)
  })

  it('says so when the clue has no audio yet', async () => {
    fetchClueAudio.mockRejectedValue(Object.assign(new Error('Request failed (404)'), { status: 404 }))
    const wrapper = await mountLoaded()

    expect(wrapper.text()).toContain('No audio for this clue yet.')
    expect(playButton(wrapper).attributes('disabled')).toBeDefined()
  })

  it('offers a retry when the audio fails to load', async () => {
    fetchClueAudio.mockRejectedValueOnce(Object.assign(new Error('Request failed (500)'), { status: 500 }))
    const wrapper = await mountLoaded()
    expect(wrapper.text()).toContain("Couldn't load the audio.")

    await wrapper.find('.btn').trigger('click')
    await flushPromises()

    expect(fetchClueAudio).toHaveBeenCalledTimes(2)
    expect(playButton(wrapper).attributes('disabled')).toBeUndefined()
  })

  it('shows an error when the browser refuses to play', async () => {
    play.mockRejectedValue(new Error('NotAllowedError'))
    const wrapper = await mountLoaded()

    await playButton(wrapper).trigger('click')
    await flushPromises()

    expect(wrapper.text()).toContain("Couldn't play the audio.")
  })

  it('loads the new audio and frees the old when the clue changes', async () => {
    const wrapper = await mountLoaded(11)

    await wrapper.setProps({ clueId: 12 })
    await flushPromises()

    expect(fetchClueAudio).toHaveBeenLastCalledWith(12)
    expect(URL.revokeObjectURL).toHaveBeenCalledWith('blob:audio')
  })

  it('frees the audio when it goes away', async () => {
    const wrapper = await mountLoaded()

    wrapper.unmount()

    expect(URL.revokeObjectURL).toHaveBeenCalledWith('blob:audio')
  })

  it('shows the clue room for testing in development', async () => {
    get.mockResolvedValue({ room: 'LIB 312' })
    const wrapper = await mountLoaded()

    expect(get).toHaveBeenCalledWith('/dev/clues/11/room')
    expect(wrapper.text()).toContain('Test mode · Room LIB 312')
  })

  it('shows no room outside development', async () => {
    const wrapper = await mountLoaded()

    expect(wrapper.text()).not.toContain('Test mode')
  })
})