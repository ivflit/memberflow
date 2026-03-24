import axios from 'axios'

const client = axios.create({
  baseURL: '',
  headers: {
    'Content-Type': 'application/json',
    'X-Tenant-Slug': import.meta.env.VITE_TENANT_SLUG || 'test-club',
  },
})

// Request interceptor — attach access token if present
client.interceptors.request.use(async (config) => {
  try {
    const { useAuthStore } = await import('../stores/auth.js')
    const authStore = useAuthStore()
    if (authStore.accessToken) {
      config.headers['Authorization'] = `Bearer ${authStore.accessToken}`
    }
  } catch {
    // Store not yet initialised
  }
  return config
})

// Response interceptor — silent refresh on 401
let isRefreshing = false
let failedQueue = []

function processQueue(error, token = null) {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error)
    } else {
      prom.resolve(token)
    }
  })
  failedQueue = []
}

async function forceLogout() {
  try {
    const { useAuthStore } = await import('../stores/auth.js')
    const authStore = useAuthStore()
    authStore.accessToken = null
    authStore.user = null
  } catch {
    // ignore
  }
  localStorage.removeItem('mf_refresh_token')
  try {
    const { default: router } = await import('../router/index.js')
    router.push('/login')
  } catch {
    // ignore
  }
}

client.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    // Do not retry the refresh endpoint itself to prevent infinite loops
    if (originalRequest?.url?.includes('/api/v1/auth/token/refresh/')) {
      return Promise.reject(error)
    }

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        }).then((token) => {
          originalRequest.headers['Authorization'] = `Bearer ${token}`
          return client(originalRequest)
        }).catch((err) => Promise.reject(err))
      }

      isRefreshing = true

      const refreshToken = localStorage.getItem('mf_refresh_token')
      if (!refreshToken) {
        isRefreshing = false
        await forceLogout()
        return Promise.reject(error)
      }

      try {
        const { data } = await axios.post('/api/v1/auth/token/refresh/', {
          refresh: refreshToken,
        }, {
          headers: {
            'Content-Type': 'application/json',
            'X-Tenant-Slug': import.meta.env.VITE_TENANT_SLUG || 'test-club',
          },
        })

        const { useAuthStore } = await import('../stores/auth.js')
        const authStore = useAuthStore()
        authStore.setTokens({
          access: data.access,
          refresh: data.refresh,
          user: authStore.user,
        })

        processQueue(null, data.access)
        originalRequest.headers['Authorization'] = `Bearer ${data.access}`
        isRefreshing = false
        return client(originalRequest)
      } catch (refreshError) {
        processQueue(refreshError, null)
        isRefreshing = false
        await forceLogout()
        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  },
)

export default client
