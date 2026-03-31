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

