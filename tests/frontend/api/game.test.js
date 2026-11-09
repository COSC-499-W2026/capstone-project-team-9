import { beforeEach, describe, expect, it, vi } from 'vitest'

vi.mock('@/api/client', () => ({
  get: vi.fn().mockResolvedValue({}),
  post: vi.fn().mockResolvedValue({}),
  postForm: vi.fn().mockResolvedValue({}),
}))

import { get, post, postForm } from '@/api/client'
import {
  createGame,
  getGameLengths,
  getPlayState,
  startGame,
  startPlay,
  submitAnswer,
} from '@/api/game'

beforeEach(() => vi.clearAllMocks())

describe('game api', () => {
  it('getGameLengths() passes the combo as query params', async () => {
    await getGameLengths(1, 2)

    expect(get).toHaveBeenCalledWith('/game-lengths?language_id=1&difficulty_id=2')
  })

  it('createGame() posts the settings in the backend field names', async () => {
    await createGame({ languageId: 1, difficultyId: 2, numClues: 3 })

    expect(post).toHaveBeenCalledWith('/games', { language_id: 1, difficulty_id: 2, num_clues: 3 })
  })

  it('startPlay() posts to the game plays route', async () => {
    await startPlay(7)

    expect(post).toHaveBeenCalledWith('/games/7/plays', {})
  })

  it('getPlayState() gets the play', async () => {
    await getPlayState(5)

    expect(get).toHaveBeenCalledWith('/plays/5')
  })


  it('startGame() creates a game, starts a play and returns its id', async () => {
    post.mockImplementation(async (path) => (path === '/games' ? { id: 7 } : { play: { id: 42 } }))

    expect(await startGame({ languageId: 2, difficultyId: 1, numClues: 3 })).toBe(42)
    expect(post).toHaveBeenCalledWith('/games', { language_id: 2, difficulty_id: 1, num_clues: 3 })
    expect(post).toHaveBeenCalledWith('/games/7/plays', {})
  })

  it('submitAnswer() sends the photo and coordinates as form data', async () => {
    const photo = new Blob(['jpeg'], { type: 'image/jpeg' })

    await submitAnswer(5, 11, { photo, latitude: 49.94, longitude: -119.39 })

    const [path, form] = postForm.mock.calls[0]
    expect(path).toBe('/plays/5/clues/11/answer')
    expect(form.get('image').name).toBe('photo.jpg')
    expect(form.get('image').type).toBe('image/jpeg')
    expect(form.get('latitude')).toBe('49.94')
    expect(form.get('longitude')).toBe('-119.39')
  })
})
