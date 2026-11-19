import { describe, it, expect, vi, beforeEach } from 'vitest'

vi.mock('@/api/login.js', () => ({ getCurrentUser: vi.fn() }))
vi.mock('@/utils/auth.js', () => ({ getToken: vi.fn() }))

import { blockGuests } from '@/router/guards.js'
import { getCurrentUser } from '@/api/login.js'
import { getToken } from '@/utils/auth.js'

const COURSE_ROUTE = { name: 'courses', meta: { noGuests: true } }

describe('blockGuests', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    getToken.mockReturnValue('token')
  })

  it('allows routes without noGuests without checking the user', async () => {
    expect(await blockGuests({ name: 'play', meta: {} })).toBe(true)
    expect(getCurrentUser).not.toHaveBeenCalled()
  })

  it.each(['student', 'instructor', 'admin'])('lets a %s into course pages', async (role) => {
    getCurrentUser.mockResolvedValue({ role })
    expect(await blockGuests(COURSE_ROUTE)).toBe(true)
  })

  it('sends a guest to play', async () => {
    getCurrentUser.mockResolvedValue({ role: 'guest' })
    expect(await blockGuests(COURSE_ROUTE)).toEqual({ name: 'play' })
  })

  it('sends a logged-out user to login', async () => {
    getToken.mockReturnValue(null)
    expect(await blockGuests(COURSE_ROUTE)).toEqual({ name: 'login' })
    expect(getCurrentUser).not.toHaveBeenCalled()
  })

  it('sends a user with an invalid token to login', async () => {
    getCurrentUser.mockRejectedValue({ status: 401 })
    expect(await blockGuests(COURSE_ROUTE)).toEqual({ name: 'login' })
  })
})
