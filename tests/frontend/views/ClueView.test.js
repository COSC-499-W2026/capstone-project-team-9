import { beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'

const push = vi.fn()
vi.mock('vue-router', () => ({ useRouter: () => ({ push }) }))
vi.mock('@/api/game', () => ({
  getPlayState: vi.fn(),
}))

import { getPlayState } from '@/api/game'
import ClueView from '@/views/ClueView.vue'

const STATE = { id: 5, game_id: 1, completed: false, current_clue_id: 11, total_clues: 3, solved_clues: 0 }

const buttonWithText = (wrapper, text) => wrapper.findAll('button').find((b) => b.text() === text)

async function mountLoaded() {
  const wrapper = mount(ClueView, { props: { playId: '5' } })
  await flushPromises()
  return wrapper
}

beforeEach(() => {
  vi.resetAllMocks()
  getPlayState.mockResolvedValue(STATE)
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
})
