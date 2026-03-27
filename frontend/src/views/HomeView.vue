<template>
  <component :is="tenantStore.hasTenant ? ClubHomePage : PlatformHomePage" />
</template>

<script setup>
import { useTenantStore } from '../stores/tenant.js'
import PlatformHomePage from './PlatformHomePage.vue'
import ClubHomePage from './ClubHomePage.vue'

const tenantStore = useTenantStore()
</script>
