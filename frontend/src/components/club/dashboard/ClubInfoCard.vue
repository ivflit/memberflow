<template>
  <div class="db-card club-info-card">
    <div class="db-card-header">
      <span class="db-card-icon info-icon">
        <BuildingOfficeIcon />
      </span>
      <h2 class="db-card-title">
        Club Info
      </h2>
    </div>
    <div class="db-card-body">
      <img
        v-if="logoUrl"
        :src="logoUrl"
        :alt="clubName"
        class="club-logo"
      >
      <p class="club-name">
        {{ clubName }}
      </p>
      <p class="welcome-msg">
        Welcome to your member portal
      </p>
    </div>
  </div>
</template>

<script setup>
import { BuildingOfficeIcon } from '@heroicons/vue/24/outline'
import { useTenantStore } from '../../../stores/tenant.js'

const tenantStore = useTenantStore()
const clubName = tenantStore.brandName
const logoUrl = tenantStore.config?.branding?.logo_url ?? null
</script>

<style scoped>
.db-card {
  background: var(--db-card-bg);
  border: 1px solid var(--db-border);
  border-radius: 14px;
  padding: 1.5rem;
  height: 100%;
  transition: background 0.2s, border-color 0.2s, box-shadow 0.2s;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.db-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

.db-card-header {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  margin-bottom: 1.25rem;
}

.db-card-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 10px;
  flex-shrink: 0;
}

.db-card-icon :deep(svg) {
  width: 18px;
  height: 18px;
}

.info-icon {
  background: rgba(255, 183, 77, 0.15);
  color: #f59e0b;
}

.db-card-title {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--db-text-strong);
}

.db-card-body {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.club-logo {
  height: 44px;
  width: auto;
  object-fit: contain;
  margin-bottom: 0.25rem;
}

.club-name {
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--db-text-strong);
}

.welcome-msg {
  font-size: 0.875rem;
  color: var(--db-text-muted);
}
</style>
