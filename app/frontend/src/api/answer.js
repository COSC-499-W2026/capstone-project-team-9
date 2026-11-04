import { postForm } from './client'

/** Send the player's photo and location for a clue; resolves with {correct, message}. */
export function verifyAnswer(clueId, image, latitude, longitude) {
  const form = new FormData()
  form.append('clue_id', clueId)
  form.append('latitude', latitude)
  form.append('longitude', longitude)
  form.append('image', image)
  return postForm('/answers/verify', form)
}
