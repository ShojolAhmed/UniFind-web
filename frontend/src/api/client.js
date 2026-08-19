import axios from 'axios'

const API_URL = (
  import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api'
).replace(/\/$/, '')

const ACCESS_KEY = 'unifind_access'
const REFRESH_KEY = 'unifind_refresh'

export const tokenStore = {
  get access() {
    return localStorage.getItem(ACCESS_KEY)
  },
  get refresh() {
    return localStorage.getItem(REFRESH_KEY)
  },
  set({ access, refresh }) {
    if (access) localStorage.setItem(ACCESS_KEY, access)
    if (refresh) localStorage.setItem(REFRESH_KEY, refresh)
  },
  clear() {
    localStorage.removeItem(ACCESS_KEY)
    localStorage.removeItem(REFRESH_KEY)
  },
}

const api = axios.create({ baseURL: API_URL })

// Attach the access token to every request.
api.interceptors.request.use((config) => {
  const token = tokenStore.access
  if (token) {
    config.headers = config.headers || {}
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Transparently refresh the access token once on a 401.
let refreshPromise = null

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config
    const status = error.response?.status

    if (status === 401 && original && !original._retry && tokenStore.refresh) {
      original._retry = true
      try {
        if (!refreshPromise) {
          refreshPromise = axios
            .post(`${API_URL}/auth/token/refresh/`, {
              refresh: tokenStore.refresh,
            })
            .then((res) => {
              tokenStore.set({ access: res.data.access })
              return res.data.access
            })
            .finally(() => {
              refreshPromise = null
            })
        }
        const newAccess = await refreshPromise
        original.headers = original.headers || {}
        original.headers.Authorization = `Bearer ${newAccess}`
        return api(original)
      } catch (refreshError) {
        tokenStore.clear()
        if (typeof window !== 'undefined') {
          const path = window.location.pathname
          if (path !== '/login' && path !== '/signup') {
            window.location.assign('/login')
          }
        }
        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  }
)

// --- Endpoint helpers -------------------------------------------------------

export const authApi = {
  register: (data) => api.post('/auth/register/', data),
  login: (data) => api.post('/auth/token/', data),
  me: () => api.get('/auth/me/'),
}

export const itemsApi = {
  list: (params) => api.get('/items/', { params }),
  byUrl: (url) => api.get(url),
  get: (id) => api.get(`/items/${id}/`),
  create: (formData) => api.post('/items/', formData),
  update: (id, formData) => api.patch(`/items/${id}/`, formData),
  remove: (id) => api.delete(`/items/${id}/`),
  claim: (id) => api.post(`/items/${id}/claim/`),
}

export const claimsApi = {
  mine: (params) => api.get('/claims/', { params }),
  approve: (id) => api.post(`/claims/${id}/approve/`),
  reject: (id) => api.post(`/claims/${id}/reject/`),
}

export const notificationsApi = {
  list: () => api.get('/notifications/'),
  read: (id) => api.post(`/notifications/${id}/read/`),
  readAll: () => api.post('/notifications/read-all/'),
  unreadCount: () => api.get('/notifications/unread-count/'),
}

// Unwrap DRF pagination (or a plain array) into a list.
export function unwrap(response) {
  const data = response.data
  if (Array.isArray(data)) return data
  return data?.results ?? data
}

// Turn a DRF error payload into a readable string.
export function apiError(error, fallback = 'Something went wrong. Please try again.') {
  const data = error?.response?.data
  if (!data) return error?.message || fallback
  if (typeof data === 'string') return data
  if (data.detail) return data.detail

  const parts = []
  for (const [key, value] of Object.entries(data)) {
    const text = Array.isArray(value) ? value.join(' ') : String(value)
    parts.push(key === 'non_field_errors' ? text : `${key}: ${text}`)
  }
  return parts.join(' ') || fallback
}

export default api
