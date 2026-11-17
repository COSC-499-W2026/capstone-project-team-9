import { afterEach, describe, expect, it, vi } from 'vitest'
import { fetchClueAudio } from '@/api/clue'

afterEach(() => vi.unstubAllGlobals())

describe('fetchClueAudio', () => {
  it('fetches the clue audio route and resolves with the blob', async () => {
    const mp3 = new Blob(['mp3'], { type: 'audio/mpeg' })
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, blob: async () => mp3 })
    vi.stubGlobal('fetch', fetchMock)

    expect(await fetchClueAudio(7)).toBe(mp3)
    expect(fetchMock).toHaveBeenCalledWith('/api/clues/7/audio')
  })

  it('throws an error carrying the status when the request fails', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: false, status: 404 }))

    await expect(fetchClueAudio(7)).rejects.toMatchObject({ status: 404, message: 'Request failed (404)' })
  })
})