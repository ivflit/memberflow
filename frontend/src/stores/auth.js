import { defineStore } from 'pinia'
import client from '../api/client.js'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    accessToken: null,
    user: null,
  }),

  getters: {
    isAuthenticated: (state) => !!state.accessToken,
    isOrgAdmin: (state) =>
      state.user?.role === 'org_admin' || state.user?.role === 'org_staff',
  },

  actions: {
    setTokens({ access, refresh, user }) {
      this.accessToken = access
      this.user = user
      if (refresh) {
        localStorage.setItem('mf_refresh_token', refresh)
      }
    },

    async login(email, password) {
      const { data } = await client.post('/api/v1/auth/login/', { email, password })
      this.setTokens(data)
      return data
    },

    async register(payload) {
      const { data } = await client.post('/api/v1/auth/register/', payload)
      this.setTokens(data)
      return data
    },

    async logout() {
      const refresh = localStorage.getItem('mf_refresh_token')
      if (refresh) {
        try {
          await client.post('/api/v1/auth/logout/', { refresh })
        } catch {
          // Ignore errors on logout
        }
      }
      this.accessToken = null
      this.user = null
      localStorage.removeItem('mf_refresh_token')
    },
  },
})
