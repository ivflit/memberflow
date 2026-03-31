<template>
  <div class="auth-page">
    <ClubNavbar />
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
import { computed } from 'vue'
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
</script>
