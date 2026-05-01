function getCookie(name) {
  if (typeof document === 'undefined') {
    return null
  }

  const cookie = document.cookie
    .split('; ')
    .find((entry) => entry.startsWith(`${name}=`))

  return cookie ? decodeURIComponent(cookie.split('=').slice(1).join('=')) : null
}

export async function apiFetch(path, options = {}) {
  const method = (options.method || 'GET').toUpperCase()
  const isFormData = options.body instanceof FormData
  const headers = {
    ...(options.headers || {}),
  }

  if (!isFormData) {
    headers['Content-Type'] = 'application/json'
  }

  if (!['GET', 'HEAD', 'OPTIONS', 'TRACE'].includes(method)) {
    const csrfToken = getCookie('csrftoken')
    if (csrfToken) {
      headers['X-CSRFToken'] = csrfToken
    }
  }

  const response = await fetch(path, {
    ...options,
    method,
    headers,
    credentials: 'include',
  })

  if (response.status === 204) {
    return null
  }

  const payload = await response.json()

  if (!response.ok) {
    throw new Error(payload.message || 'Request failed.')
  }

  return payload
}
