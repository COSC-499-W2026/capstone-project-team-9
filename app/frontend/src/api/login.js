import { postForm } from './client.js'

/** Exchange email + password for a token. Resolves with {access_token, token_type}. */
export function requestToken(email, password) {
  const form = new FormData()
  form.append('username', email) // the OAuth2 password flow calls the email field "username"
  form.append('password', password)
  return postForm('/login/token', form)
}