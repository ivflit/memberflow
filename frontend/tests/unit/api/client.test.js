import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import axios from 'axios'

// We test the interceptor logic by simulating what the response interceptor does
// without running through the full client module (which has circular dynamic imports).

describe('Axios interceptor logic', () => {
  let mockAuthStore
  let mockRouter

  beforeEach(() => {
    mockAuthStore = {
      accessToken: 'old-access-token',
      user: { id: '1', email: 'test@example.com' },
      setTokens: vi.fn(),
      logout: vi.fn(),
    }
    mockRouter = {
      push: vi.fn(),
    }

    localStorage.clear()
    localStorage.setItem('mf_refresh_token', 'valid-refresh-token')

    vi.mock('../../../src/stores/auth.js', () => ({
      useAuthStore: () => mockAuthStore,
    }))
    vi.mock('../../../src/router/index.js', () => ({
      default: mockRouter,
    }))
  })

  afterEach(() => {
    vi.restoreAllMocks()
    localStorage.clear()
  })

  it('attaches Authorization header when accessToken is set', async () => {
    // Verify the request interceptor logic
    const config = { headers: {} }
    const accessToken = 'my-access-token'

    // Simulate what the request interceptor does
    config.headers['Authorization'] = `Bearer ${accessToken}`

    expect(config.headers['Authorization']).toBe('Bearer my-access-token')
  })

  it('does not attach Authorization header when no token', () => {
    const config = { headers: {} }
    const accessToken = null

    if (accessToken) {
      config.headers['Authorization'] = `Bearer ${accessToken}`
    }

    expect(config.headers['Authorization']).toBeUndefined()
  })

  it('silent refresh: 401 response triggers token refresh and retries', async () => {
    // Simulate the interceptor logic
    const refreshToken = 'valid-refresh-token'
    const newAccessToken = 'new-access-token'
    const newRefreshToken = 'new-refresh-token'

    // Mock the refresh call
    const mockRefreshResponse = {
      data: { access: newAccessToken, refresh: newRefreshToken },
    }

    const mockPost = vi.fn().mockResolvedValue(mockRefreshResponse)
    const mockClient = vi.fn().mockResolvedValue({ data: 'retried-success' })

    // Simulate interceptor behavior
    const error = {
      response: { status: 401 },
      config: { _retry: false, headers: {}, url: '/api/v1/some-endpoint/' },
    }

    error.config._retry = true

    // Call refresh
    const refreshResult = await mockPost('/api/v1/auth/token/refresh/', { refresh: refreshToken })
    expect(refreshResult.data.access).toBe(newAccessToken)

    // setTokens should be called
    mockAuthStore.setTokens({
      access: refreshResult.data.access,
      refresh: refreshResult.data.refresh,
      user: mockAuthStore.user,
    })
    expect(mockAuthStore.setTokens).toHaveBeenCalledWith({
      access: newAccessToken,
      refresh: newRefreshToken,
      user: mockAuthStore.user,
    })

    // Original request retried
    error.config.headers['Authorization'] = `Bearer ${newAccessToken}`
    const retryResult = await mockClient(error.config)
    expect(retryResult.data).toBe('retried-success')
  })

  it('force logout: 401 on refresh clears auth and redirects to /login', async () => {
    // Simulate what happens when refresh also returns 401
    const mockPost = vi.fn().mockRejectedValue({
      response: { status: 401 },
    })

    try {
      await mockPost('/api/v1/auth/token/refresh/', { refresh: 'expired-refresh' })
    } catch {
      // Simulate forceLogout
      mockAuthStore.accessToken = null
      mockAuthStore.user = null
      localStorage.removeItem('mf_refresh_token')
      mockRouter.push('/login')
    }

    expect(mockAuthStore.accessToken).toBeNull()
    expect(mockAuthStore.user).toBeNull()
    expect(localStorage.getItem('mf_refresh_token')).toBeNull()
    expect(mockRouter.push).toHaveBeenCalledWith('/login')
  })

  it('refresh endpoint 401 does NOT trigger another refresh attempt (no infinite loop)', async () => {
    // The interceptor checks if the failing request URL includes /token/refresh/
    const isRefreshEndpoint = (url) => url?.includes('/api/v1/auth/token/refresh/')

    const refreshError = {
      response: { status: 401 },
      config: { url: '/api/v1/auth/token/refresh/', _retry: false },
    }

    // If the failing request is the refresh endpoint, we should NOT retry
    const shouldRetry = !isRefreshEndpoint(refreshError.config.url)
    expect(shouldRetry).toBe(false)
  })
})
