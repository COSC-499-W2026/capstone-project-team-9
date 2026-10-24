import { afterEach, describe, expect, it, vi } from 'vitest'
import { get, post } from '../../src/api/client'

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
})