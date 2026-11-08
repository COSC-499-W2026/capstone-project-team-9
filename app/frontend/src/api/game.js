import { get, post } from './client'

// ---------- Game options ----------

export const getLanguages = () => get('/languages')

export const getDifficulties = () => get('/difficulties')

/** {min, max} clues a game can have for this combo. {0, 0} means no game can be made. */
export const getGameLengths = (languageId, difficultyId) =>
  get(`/game-lengths?language_id=${languageId}&difficulty_id=${difficultyId}`)

// ---------- Games and plays ----------

export const createGame = ({ languageId, difficultyId, numClues }) =>
  post('/games', { language_id: languageId, difficulty_id: difficultyId, num_clues: numClues })

/** Resolves with {play, clues}. */
export const startPlay = (gameId) => post(`/games/${gameId}/plays`, {})

/** Resolves with {id, game_id, completed, current_clue_id, total_clues, solved_clues}. */
export const getPlayState = (playId) => get(`/plays/${playId}`)

/** Create a game with these settings, start a play of it, and resolve with the play id. */
export async function startGame(settings) {
  const game = await createGame(settings)
  const { play } = await startPlay(game.id)
  return play.id
}

// ---------- Clue audio ----------

// TODO: the backend doesn't serve clue audio yet. This is the URL the player will load once
// an endpoint exists; until then the player shows an "audio unavailable" state.
export const clueAudioUrl = (clueId) => `/api/clues/${clueId}/audio`
