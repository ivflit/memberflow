<template>
  <div
    class="auth-page"
    :data-theme="theme"
  >
    <ClubNavbar
      :is-dark="theme === 'dark'"
      @toggle-theme="toggleTheme"
    />
    <div class="auth-content">
      <div class="auth-card">
        <div class="auth-brand">
          <img
            v-if="logoUrl"
            :src="logoUrl"
            :alt="clubName"
            class="auth-logo"
          >
          <div
            v-else
            class="auth-initials"
            aria-hidden="true"
          >
            {{ initials }}
          </div>
          <p class="auth-club-name">
            {{ clubName }}
          </p>
        </div>
        <hr class="auth-divider">
        <slot />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import ClubNavbar from './ClubNavbar.vue'
import { useTenantStore } from '../../stores/tenant.js'

const tenantStore = useTenantStore()
const clubName = tenantStore.brandName
const logoUrl = tenantStore.config?.branding?.logo_url ?? null

const initials = computed(() =>
  clubName
    .split(' ')
    .slice(0, 2)
    .map((w) => w[0]?.toUpperCase() ?? '')
    .join(''),
)

const theme = ref(localStorage.getItem('mf-theme') || 'light')

function toggleTheme() {
  theme.value = theme.value === 'dark' ? 'light' : 'dark'
  localStorage.setItem('mf-theme', theme.value)
}
</script>
