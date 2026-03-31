<template>
  <div
    v-if="isDev"
    class="dev-toggle"
  >
    <button
      class="dev-toggle-btn"
      :title="label"
      @click="toggle"
    >
      <span class="dev-badge">DEV</span>
      <span class="dev-label">{{ label }}</span>
    </button>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useTenantStore } from '../stores/tenant.js'

const isDev = import.meta.env.DEV

const tenantStore = useTenantStore()

const label = computed(() => tenantStore.hasTenant ? 'View platform page' : 'View club page')

function toggle() {
  tenantStore._devForceTenant = !tenantStore.hasTenant
}
</script>
