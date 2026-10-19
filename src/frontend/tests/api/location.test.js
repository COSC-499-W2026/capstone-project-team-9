import { describe, expect, it, vi } from 'vitest'

vi.mock('../../src/api/client', () => ({ post: vi.fn().mockResolvedValue({ allowed: true }) }))

import { post } from '../../src/api/client'
import { verifyLocation } from '../../src/api/location'

describe('verifyLocation', () => {
  it('posts the coordinates to /location/verify', async () => {
    const result = await verifyLocation(49.9, -119.4)

    expect(post).toHaveBeenCalledWith('/location/verify', { latitude: 49.9, longitude: -119.4 })
    expect(result).toEqual({ allowed: true })
  })
})