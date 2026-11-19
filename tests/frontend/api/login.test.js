import { describe, it, expect, vi, beforeEach } from 'vitest'
import { get, post, postForm } from '@/api/client.js'
import { requestToken, requestGuestToken, getCurrentUser } from '@/api/login.js'

vi.mock('@/api/client.js', () => ({
  get: vi.fn(),
  post: vi.fn(),
  postForm: vi.fn(),
}))

beforeEach(() => {
  vi.clearAllMocks()
})

describe('requestToken', () => {
  it('posts the email as "username" plus the password to /login/token and returns the token', async () => {
    const response = { access_token: 'abc', token_type: 'bearer' }
    postForm.mockResolvedValue(response)

    await expect(requestToken('user@example.com', 'hunter2')).resolves.toEqual(response)

    const [path, form] = postForm.mock.calls[0]
    expect(path).toBe('/login/token')
    expect(form).toBeInstanceOf(FormData)
    expect(Object.fromEntries(form)).toEqual({
      username: 'user@example.com',
      password: 'hunter2',
    })
  })

  it('propagates request errors', async () => {
    const err = Object.assign(new Error('Request failed (401)'), { status: 401 })
    postForm.mockRejectedValue(err)

    await expect(requestToken('user@example.com', 'wrong')).rejects.toBe(err)
  })
})

describe('requestGuestToken', () => {
  it('posts an empty object to /login/guest and returns the token', async () => {
    const response = { access_token: 'guest', token_type: 'bearer' }
    post.mockResolvedValue(response)

    await expect(requestGuestToken()).resolves.toEqual(response)
    expect(post).toHaveBeenCalledWith('/login/guest', {})
  })
})

describe('getCurrentUser', () => {
  it('requests /login/me and returns the user', async () => {
    const user = { name: 'Ada', email: 'ada@example.com', role: 'admin' }
    get.mockResolvedValue(user)

    await expect(getCurrentUser()).resolves.toEqual(user)
    expect(get).toHaveBeenCalledWith('/login/me')
  })
})