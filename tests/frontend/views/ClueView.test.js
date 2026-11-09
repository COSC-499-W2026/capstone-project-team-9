import { beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import { h } from 'vue'

const push = vi.fn()
vi.mock('vue-router', () => ({ useRouter: () => ({ push }) }))
vi.mock('@/api/game', () => ({
  getPlayState: vi.fn(),
  submitAnswer: vi.fn(),
}))
// The audio placeholder looks up a testing-only room; behave like outside development
vi.mock('@/api/client', () => ({ get: vi.fn().mockRejectedValue(new Error('Request failed (404)')) }))
vi.mock('@/utils/geolocation', () => ({ getCurrentCoords: vi.fn() }))

import { getPlayState, submitAnswer } from '@/api/game'
import { getCurrentCoords } from '@/utils/geolocation'
import ClueView from '@/views/ClueView.vue'

const STATE = { id: 5, game_id: 1, completed: false, current_clue_id: 11, total_clues: 3, solved_clues: 0 }
const PHOTO = new Blob(['jpeg'], { type: 'image/jpeg' })

// The real camera is tested on its own; here a button stands in for "the player took a photo"
const CameraStub = {
  props: ['modelValue'],
  emits: ['update:modelValue'],
  setup: (props, { emit }) => () =>
    h('button', { class: 'fake-shutter', onClick: () => emit('update:modelValue', PHOTO) }, 'snap'),
}

const submitButton = (wrapper) => wrapper.findAll('button').find((b) => b.text().includes('Submit answer') || b.text().includes('Checking'))

const buttonWithText = (wrapper, text) => wrapper.findAll('button').find((b) => b.text() === text)

async function mountLoaded() {
  const wrapper = mount(ClueView, { props: { playId: '5' }, global: { stubs: { CameraCapture: CameraStub } } })
  await flushPromises()
  return wrapper
}

async function takePhotoAndSubmit(wrapper) {
  await wrapper.find('.fake-shutter').trigger('click')
  await submitButton(wrapper).trigger('click')
  await flushPromises()
}

beforeEach(() => {
  vi.resetAllMocks()
  getPlayState.mockResolvedValue(STATE)
  getCurrentCoords.mockResolvedValue({ latitude: 49.94, longitude: -119.39 })
})

describe('ClueView', () => {
  it('loads the play and shows progress for the first clue', async () => {
    const wrapper = await mountLoaded()

    expect(getPlayState).toHaveBeenCalledWith('5')
    expect(wrapper.text()).toContain('Clue 1 of 3')
  })

  it('numbers the clue by how many are solved', async () => {
    getPlayState.mockResolvedValue({ ...STATE, current_clue_id: 14, solved_clues: 2 })
    const wrapper = await mountLoaded()

    expect(wrapper.text()).toContain('Clue 3 of 3')
  })

  it('shows the audio placeholder', async () => {
    const wrapper = await mountLoaded()

    expect(wrapper.text()).toContain('Clue audio coming soon')
  })

  it('shows a Skip button that is disabled until the backend supports skipping', async () => {
    const wrapper = await mountLoaded()

    const skip = buttonWithText(wrapper, 'Skip')
    expect(skip.exists()).toBe(true)
    expect(skip.attributes('disabled')).toBeDefined()
  })

  it('shows the finish screen when the play is complete', async () => {
    getPlayState.mockResolvedValue({ ...STATE, completed: true, current_clue_id: null, solved_clues: 3 })
    const wrapper = await mountLoaded()

    expect(wrapper.text()).toContain('You found them all')
    await buttonWithText(wrapper, 'Play again').trigger('click')
    expect(push).toHaveBeenCalledWith({ name: 'play' })
  })

  it('goes back to the start screen from the exit button', async () => {
    const wrapper = await mountLoaded()

    await wrapper.find('[aria-label="Exit game"]').trigger('click')

    expect(push).toHaveBeenCalledWith({ name: 'play' })
  })

  it('shows a message when the play does not exist', async () => {
    getPlayState.mockRejectedValue(Object.assign(new Error('Request failed (404)'), { status: 404 }))
    const wrapper = await mountLoaded()

    expect(wrapper.text()).toContain("This game doesn't exist")
  })

  it('shows a message when the play fails to load', async () => {
    getPlayState.mockRejectedValue(Object.assign(new Error('Request failed (500)'), { status: 500 }))
    const wrapper = await mountLoaded()

    expect(wrapper.text()).toContain("Couldn't load your game")
  })

  it('keeps Submit disabled until a photo is taken', async () => {
    const wrapper = await mountLoaded()
    expect(submitButton(wrapper).attributes('disabled')).toBeDefined()

    await wrapper.find('.fake-shutter').trigger('click')

    expect(submitButton(wrapper).attributes('disabled')).toBeUndefined()
  })

  it('sends the photo and location for the current clue to the checker', async () => {
    submitAnswer.mockResolvedValue({ correct: true, message: 'Correct answer!', attempts: 1, play_complete: false })
    const wrapper = await mountLoaded()

    await takePhotoAndSubmit(wrapper)

    expect(submitAnswer).toHaveBeenCalledWith('5', 11, { photo: PHOTO, latitude: 49.94, longitude: -119.39 })
  })

  it('shows Checking while the answer is being checked', async () => {
    submitAnswer.mockReturnValue(new Promise(() => {})) // never resolves
    const wrapper = await mountLoaded()

    await takePhotoAndSubmit(wrapper)

    expect(submitButton(wrapper).text()).toContain('Checking')
    expect(submitButton(wrapper).attributes('disabled')).toBeDefined()
  })

  it('moves on to the next clue after a correct answer', async () => {
    submitAnswer.mockResolvedValue({ correct: true, message: 'Correct answer!', attempts: 1, play_complete: false })
    const wrapper = await mountLoaded()
    await takePhotoAndSubmit(wrapper)

    expect(wrapper.text()).toContain('Correct!')
    getPlayState.mockResolvedValue({ ...STATE, current_clue_id: 12, solved_clues: 1 })
    await buttonWithText(wrapper, 'Next clue').trigger('click')
    await flushPromises()

    expect(wrapper.text()).toContain('Clue 2 of 3')
  })

  it('lets the player try again after a wrong answer', async () => {
    submitAnswer.mockResolvedValue({ correct: false, message: 'Wrong answer. Try again.', attempts: 2, play_complete: false })
    const wrapper = await mountLoaded()
    await takePhotoAndSubmit(wrapper)

    expect(wrapper.text()).toContain('Not quite')
    expect(wrapper.text()).toContain('Wrong answer. Try again.')
    expect(wrapper.text()).toContain('2 attempts')
    await buttonWithText(wrapper, 'Try again').trigger('click')
    await flushPromises()

    expect(getPlayState).toHaveBeenCalledTimes(1) // same clue, no reload
    expect(submitButton(wrapper).attributes('disabled')).toBeDefined() // photo cleared
  })

  it('shows the finish screen after the last correct answer', async () => {
    submitAnswer.mockResolvedValue({ correct: true, message: 'Correct answer!', attempts: 1, play_complete: true })
    const wrapper = await mountLoaded()
    await takePhotoAndSubmit(wrapper)

    getPlayState.mockResolvedValue({ ...STATE, completed: true, current_clue_id: null, solved_clues: 3 })
    await buttonWithText(wrapper, 'See results').trigger('click')
    await flushPromises()

    expect(wrapper.text()).toContain('You found them all')
  })

  it('explains when location access is denied', async () => {
    getCurrentCoords.mockRejectedValue({ code: 1, message: 'User denied Geolocation' })
    const wrapper = await mountLoaded()

    await takePhotoAndSubmit(wrapper)

    expect(wrapper.text()).toContain('Location access is needed')
    expect(submitAnswer).not.toHaveBeenCalled()
  })

  it('shows the backend reason when the photo is rejected', async () => {
    submitAnswer.mockRejectedValue(Object.assign(new Error('Request failed (413)'), { status: 413, detail: 'Image too large' }))
    const wrapper = await mountLoaded()

    await takePhotoAndSubmit(wrapper)

    expect(wrapper.text()).toContain('Image too large')
  })

  it('reloads the play when the clue was already answered', async () => {
    submitAnswer.mockRejectedValue(Object.assign(new Error('Request failed (409)'), { status: 409 }))
    const wrapper = await mountLoaded()

    getPlayState.mockResolvedValue({ ...STATE, current_clue_id: 12, solved_clues: 1 })
    await takePhotoAndSubmit(wrapper)

    expect(wrapper.text()).toContain('Clue 2 of 3')
  })

})
