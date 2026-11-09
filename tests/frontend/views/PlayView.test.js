import { beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'

const push = vi.fn()
vi.mock('vue-router', () => ({ useRouter: () => ({ push }) }))
vi.mock('@/api/location', () => ({ verifyLocation: vi.fn() }))
vi.mock('@/api/game', () => ({
  getLanguages: vi.fn(),
  getDifficulties: vi.fn(),
  getGameLengths: vi.fn(),
  startGame: vi.fn(),
}))
vi.mock('@/utils/geolocation', () => ({ getCurrentCoords: vi.fn() }))

import { verifyLocation } from '@/api/location'
import { getDifficulties, getGameLengths, getLanguages, startGame } from '@/api/game'
import { getCurrentCoords } from '@/utils/geolocation'
import PlayView from '@/views/PlayView.vue'

// Mount and wait for the dropdown options to load
async function mountLoaded() {
  const wrapper = mount(PlayView)
  await flushPromises()
  return wrapper
}

async function clickPlay(wrapper) {
  await wrapper.find('button').trigger('click')
  await flushPromises()
}

beforeEach(() => {
  vi.resetAllMocks()
  getCurrentCoords.mockResolvedValue({ latitude: 49.9, longitude: -119.4 })
  getLanguages.mockResolvedValue([
    { id: 2, name: 'French' },
    { id: 1, name: 'Spanish' },
  ])
  getDifficulties.mockResolvedValue([
    { id: 10, name: 'Easy' },
    { id: 11, name: 'Hard' },
  ])
  getGameLengths.mockResolvedValue({ min: 1, max: 6 })
  startGame.mockResolvedValue(42)
})

describe('PlayView', () => {
  it('shows the allowed message on campus', async () => {
    verifyLocation.mockResolvedValue({ allowed: true, message: 'Location verified.' })
    const wrapper = await mountLoaded()

    await clickPlay(wrapper)

    expect(wrapper.text()).toContain('✅')
    expect(wrapper.text()).toContain('Location verified.')
  })

  it('shows the blocked message off campus', async () => {
    verifyLocation.mockResolvedValue({ allowed: false, message: 'Head to campus!' })
    const wrapper = await mountLoaded()

    await clickPlay(wrapper)

    expect(wrapper.text()).toContain('🚫')
    expect(wrapper.text()).toContain('Head to campus!')
  })

  it('sends the device coordinates to the API', async () => {
    verifyLocation.mockResolvedValue({ allowed: true, message: 'ok' })

    await clickPlay(await mountLoaded())

    expect(verifyLocation).toHaveBeenCalledWith(49.9, -119.4)
  })

  it('shows an error when location access fails', async () => {
    getCurrentCoords.mockRejectedValue(new Error('User denied Geolocation'))
    const wrapper = await mountLoaded()

    await clickPlay(wrapper)

    expect(wrapper.text()).toContain('User denied Geolocation')
    expect(verifyLocation).not.toHaveBeenCalled()
  })

  it('shows an error when the backend call fails', async () => {
    verifyLocation.mockRejectedValue(new Error('Request failed (500)'))
    const wrapper = await mountLoaded()

    await clickPlay(wrapper)

    expect(wrapper.text()).toContain('Request failed (500)')
  })

  it('disables the button while waiting', async () => {
    verifyLocation.mockReturnValue(new Promise(() => {})) // never resolves
    const wrapper = await mountLoaded()

    await wrapper.find('button').trigger('click')

    expect(wrapper.find('button').attributes('disabled')).toBeDefined()
  })

  it('starts a game and opens the first clue when on campus', async () => {
    verifyLocation.mockResolvedValue({ allowed: true, message: 'Location verified.' })

    await clickPlay(await mountLoaded())

    expect(startGame).toHaveBeenCalledWith({ languageId: 2, difficultyId: 10, numClues: 3 })
    expect(push).toHaveBeenCalledWith({ name: 'clue', params: { playId: 42 } })
  })

  it('does not start a game off campus', async () => {
    verifyLocation.mockResolvedValue({ allowed: false, message: 'Head to campus!' })

    await clickPlay(await mountLoaded())

    expect(startGame).not.toHaveBeenCalled()
    expect(push).not.toHaveBeenCalled()
  })

  it('shows the reason when the game cannot be started', async () => {
    verifyLocation.mockResolvedValue({ allowed: true, message: 'Location verified.' })
    startGame.mockRejectedValue(Object.assign(new Error('Request failed (422)'), { detail: 'Not enough clues available' }))
    const wrapper = await mountLoaded()

    await clickPlay(wrapper)

    expect(wrapper.text()).toContain('Not enough clues available')
    expect(push).not.toHaveBeenCalled()
  })

  it('lists the languages and the available question counts', async () => {
    const wrapper = await mountLoaded()

    const languages = wrapper.findAll('#language option').map((o) => o.text())
    const counts = wrapper.findAll('#num-clues option').map((o) => o.text())
    expect(languages).toEqual(['French', 'Spanish'])
    expect(counts).toEqual(['1', '2', '3', '4', '5', '6'])
    expect(getGameLengths).toHaveBeenCalledWith(2, 10)
  })

  it('starts the game with the picked language and question count', async () => {
    verifyLocation.mockResolvedValue({ allowed: true, message: 'Location verified.' })
    const wrapper = await mountLoaded()

    getGameLengths.mockResolvedValue({ min: 1, max: 4 })
    await wrapper.find('#language').setValue(1)
    await flushPromises()
    await wrapper.find('#num-clues').setValue(4)
    await clickPlay(wrapper)

    expect(getGameLengths).toHaveBeenCalledWith(1, 10)
    expect(startGame).toHaveBeenCalledWith({ languageId: 1, difficultyId: 10, numClues: 4 })
  })

  it('defaults to fewer questions when fewer are available', async () => {
    getGameLengths.mockResolvedValue({ min: 1, max: 2 })
    const wrapper = await mountLoaded()

    expect(wrapper.find('#num-clues').element.value).toBe('2')
  })

  it('does not start a game when the language has no questions', async () => {
    verifyLocation.mockResolvedValue({ allowed: true, message: 'Location verified.' })
    getGameLengths.mockResolvedValue({ min: 0, max: 0 })
    const wrapper = await mountLoaded()

    expect(wrapper.find('#num-clues').text()).toContain('None available')
    await clickPlay(wrapper)

    expect(wrapper.text()).toContain('No questions available for this language and difficulty yet.')
    expect(startGame).not.toHaveBeenCalled()
  })

  it('shows an error when the options fail to load', async () => {
    getLanguages.mockRejectedValue(new Error('Request failed (500)'))
    const wrapper = await mountLoaded()

    expect(wrapper.text()).toContain("Couldn't load game options.")
  })

  it('lists the difficulties', async () => {
    const wrapper = await mountLoaded()

    expect(wrapper.findAll('#difficulty option').map((o) => o.text())).toEqual(['Easy', 'Hard'])
  })

  it('starts the game with the picked difficulty', async () => {
    verifyLocation.mockResolvedValue({ allowed: true, message: 'Location verified.' })
    const wrapper = await mountLoaded()

    await wrapper.find('#difficulty').setValue(11)
    await flushPromises()
    await clickPlay(wrapper)

    expect(getGameLengths).toHaveBeenCalledWith(2, 11)
    expect(startGame).toHaveBeenCalledWith({ languageId: 2, difficultyId: 11, numClues: 3 })
  })
})
