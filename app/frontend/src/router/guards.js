import { getCurrentUser } from '../api/course'
import { getToken } from '../utils/auth'

/**
 * Router guard for routes with `meta.noGuests`: guests go to play, logged-out users go to login.
 * Returns true to allow the navigation, or a route to redirect to.
 */
export async function blockGuests(to) {
  if (!to.meta.noGuests) return true
  if (!getToken()) return { name: 'login' }
  try {
    const user = await getCurrentUser()
    return user.role === 'guest' ? { name: 'play' } : true
  } catch {
    return { name: 'login' } // token expired or invalid
  }
}
