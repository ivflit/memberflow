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

<style scoped>
.dev-toggle {
  position: fixed;
  bottom: 1.25rem;
  right: 1.25rem;
  z-index: 9999;
}

.dev-toggle-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: #1e1e2e;
  color: #cdd6f4;
  border: 1px solid #45475a;
  border-radius: 8px;
  padding: 0.45rem 0.85rem;
  font-size: 0.8rem;
  font-family: ui-monospace, monospace;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.35);
  transition: background 0.15s ease, transform 0.1s ease;
}

.dev-toggle-btn:hover {
  background: #313244;
  transform: translateY(-1px);
}

.dev-badge {
  background: #f38ba8;
  color: #1e1e2e;
  font-size: 0.65rem;
  font-weight: 700;
  padding: 0.1rem 0.35rem;
  border-radius: 4px;
  letter-spacing: 0.05em;
}

.dev-label {
  white-space: nowrap;
}
</style>
