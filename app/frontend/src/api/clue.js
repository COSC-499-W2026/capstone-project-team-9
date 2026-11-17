/** Resolves with the clue's audio as an mp3 Blob. Rejects with an error carrying `status` if it can't be loaded. */
export async function fetchClueAudio(clueId) {
  const res = await fetch(`/api/clues/${clueId}/audio`)
  if (!res.ok) {
    const err = new Error(`Request failed (${res.status})`)
    err.status = res.status
    throw err
  }
  return res.blob()
}