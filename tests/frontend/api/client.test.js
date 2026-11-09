import { afterEach, describe, expect, it, vi } from 'vitest'
import { get, post, postForm } from '@/api/client'

function mockFetch(response) {
  const fn = vi.fn().mockResolvedValue(response)
  vi.stubGlobal('fetch', fn)
  return fn
}

afterEach(() => vi.unstubAllGlobals())

describe('api client', () => {
  it('get() prefixes /api and returns parsed JSON', async () => {
    const fetchMock = mockFetch({ ok: true, json: async () => ({ status: 'ok' }) })

    expect(await get('/health')).toEqual({ status: 'ok' })
    expect(fetchMock.mock.calls[0][0]).toBe('/api/health')
  })

  it('post() sends a JSON body with the POST method', async () => {
    const fetchMock = mockFetch({ ok: true, json: async () => ({}) })

    await post('/location/verify', { latitude: 1, longitude: 2 })

    const [url, options] = fetchMock.mock.calls[0]
    expect(url).toBe('/api/location/verify')
    expect(options.method).toBe('POST')
    expect(JSON.parse(options.body)).toEqual({ latitude: 1, longitude: 2 })
  })

  it('throws when the response is not ok', async () => {
    mockFetch({ ok: false, status: 422 })

    await expect(get('/anything')).rejects.toThrow('422')
  })

  it('attaches the status and backend detail to the error', async () => {
    mockFetch({ ok: false, status: 422, json: async () => ({ detail: 'Not enough clues' }) })

    await expect(get('/anything')).rejects.toMatchObject({ status: 422, detail: 'Not enough clues' })
  })

  it('postForm() sends FormData and lets the browser set the content type', async () => {
    const fetchMock = mockFetch({ ok: true, json: async () => ({ correct: true }) })
    const form = new FormData()

    expect(await postForm('/plays/1/clues/2/answer', form)).toEqual({ correct: true })

    const [url, options] = fetchMock.mock.calls[0]
    expect(url).toBe('/api/plays/1/clues/2/answer')
    expect(options.method).toBe('POST')
    expect(options.body).toBe(form)
    expect(options.headers).toEqual({})
  })
})
