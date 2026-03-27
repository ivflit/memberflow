import { defineStore } from 'pinia'
import client from '../api/client.js'

export const useTenantStore = defineStore('tenant', {
  state: () => ({
    config: null,
    _devForceTenant: null, // null = use real config; true/false = override (dev only)
  }),

  getters: {
    hasTenant: (state) => {
      if (import.meta.env.DEV && state._devForceTenant !== null) return state._devForceTenant
      return state.config !== null
    },
    isFeatureEnabled: (state) => (flag) => state.config?.features?.[flag] ?? false,
    brandName: (state) => state.config?.name ?? 'MemberFlow',
  },

  actions: {
    async bootstrap() {
      try {
        const { data } = await client.get('/api/v1/config/')
        this.config = data
        this._applyBranding(data.branding)
      } catch {
        // No tenant in scope (root/platform domain) or config endpoint not reachable.
        // hasTenant remains false — platform marketing page will render.
        this.config = null
      }
    },

    _applyBranding(branding) {
      if (!branding) return
      const root = document.documentElement
      if (branding.primary_color) root.style.setProperty('--bulma-primary', branding.primary_color)
      if (branding.secondary_color) root.style.setProperty('--bulma-secondary', branding.secondary_color)
    },
  },
})
