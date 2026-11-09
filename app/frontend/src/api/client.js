const BASE_URL = '/api' // Vite proxies this to FastAPI (see vite.config.js)

async function request(path, options = {}) {
  const res = await fetch(BASE_URL + path, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) {
    const err = new Error(`Request failed (${res.status})`)
    err.status = res.status
    // FastAPI puts a human readable reason in `detail`; keep it for the UI if there is one
    try {
      const { detail } = await res.json()
      if (typeof detail === 'string') err.detail = detail
    } catch {
      // body wasn't JSON, the status is all we have
    }
    throw err
  }
  return res.json()
}

export const get = (path) => request(path)

export const post = (path, body) =>
  request(path, { method: 'POST', body: JSON.stringify(body) })

// Empty headers so the browser sets the multipart Content-Type (with its boundary) itself
export const postForm = (path, formData) =>
  request(path, { method: 'POST', headers: {}, body: formData })