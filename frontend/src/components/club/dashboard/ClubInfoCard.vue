<template>
  <div class="card">
    <div class="card-header">
      <p class="card-header-title">
        Club Info
      </p>
    </div>
    <div class="card-content">
      <div class="club-info-body">
        <img
          v-if="logoUrl"
          :src="logoUrl"
          :alt="clubName"
          class="club-info-logo"
        >
        <p class="has-text-weight-bold is-size-5 club-info-name">
          {{ clubName }}
        </p>
        <p class="has-text-grey">
          Welcome to your member portal
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useTenantStore } from '../../../stores/tenant.js'

const tenantStore = useTenantStore()

const clubName = tenantStore.brandName
const logoUrl = tenantStore.config?.branding?.logo_url ?? null
</script>

<style scoped>
.club-info-body {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.5rem;
}

.club-info-logo {
  height: 48px;
  width: auto;
  object-fit: contain;
}

.club-info-name {
  color: var(--mf-navy, #1b2a4a);
}
</style>
