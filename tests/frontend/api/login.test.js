import { describe, it, expect, vi, afterEach } from 'vitest'
import { get, post } from '../../../src/api/client.js'

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('API client', () => {
  it('sends a GET request', async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ message: 'Success' }),
    })

    vi.stubGlobal('fetch', mockFetch)

    const result = await get('/users')

    expect(result).toEqual({ message: 'Success' })
    expect(mockFetch).toHaveBeenCalledWith('/api/users', {
      headers: { 'Content-Type': 'application/json' },
    })
  })

  it('sends a POST request with JSON data', async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ name: 'Alice' }),
    })

    vi.stubGlobal('fetch', mockFetch)

    const result = await post('/login', {
      email: 'alice@example.com',
      password: 'StrongPass123!',
    })

    expect(result).toEqual({ name: 'Alice' })

    expect(mockFetch).toHaveBeenCalledWith('/api/login', {
      headers: { 'Content-Type': 'application/json' },
      method: 'POST',
      body: JSON.stringify({
        email: 'alice@example.com',
        password: 'StrongPass123!',
      }),
    })
  })

  it('throws an error when the request fails', async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 401,
    })

    vi.stubGlobal('fetch', mockFetch)

    await expect(
      post('/login', {
        email: 'alice@example.com',
        password: 'wrong',
      }),
    ).rejects.toThrow('Request failed (401)')
  })
})