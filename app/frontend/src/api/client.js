const BASE_URL = '/api' // Vite proxies this to FastAPI (see vite.config.js)

async function request(path, options = {}) {
  const res = await fetch(BASE_URL + path, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) {
    throw new Error(`Request failed (${res.status})`)
  }
  return res.json()
}

export const get = (path) => request(path)

export const post = (path, body) =>
  request(path, { method: 'POST', body: JSON.stringify(body) })