<template>
  <nav
    class="navbar is-fixed-top club-navbar"
    role="navigation"
    aria-label="main navigation"
  >
    <div class="container">
      <div class="navbar-brand">
        <a
          class="navbar-item club-brand"
          href="/"
        >
          <img
            v-if="logoUrl"
            :src="logoUrl"
            :alt="clubName"
            class="club-logo"
          >
          <span class="club-name">{{ clubName }}</span>
        </a>

        <a
          role="button"
          class="navbar-burger"
          :class="{ 'is-active': menuOpen }"
          aria-label="menu"
          :aria-expanded="menuOpen"
          @click="menuOpen = !menuOpen"
        >
          <span aria-hidden="true" />
          <span aria-hidden="true" />
          <span aria-hidden="true" />
        </a>
      </div>

      <div
        class="navbar-menu"
        :class="{ 'is-active': menuOpen }"
      >
        <div class="navbar-end">
          <div class="navbar-item">
            <button
              class="button is-ghost cn-theme-btn"
              :aria-label="isDark ? 'Switch to light mode' : 'Switch to dark mode'"
              @click="$emit('toggle-theme')"
            >
              <SunIcon
                v-if="isDark"
                class="cn-theme-icon"
              />
              <MoonIcon
                v-else
                class="cn-theme-icon"
              />
            </button>
          </div>
          <div class="navbar-item">
            <div class="buttons">
              <a
                class="button is-light login-btn"
                href="/login"
              >Log in</a>
              <a
                class="button is-primary join-btn"
                href="/register"
              >Join Now</a>
            </div>
          </div>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref } from 'vue'
import { SunIcon, MoonIcon } from '@heroicons/vue/24/outline'
import { useTenantStore } from '../../stores/tenant.js'

defineProps({
  isDark: {
    type: Boolean,
    default: false,
  },
})

defineEmits(['toggle-theme'])

const tenantStore = useTenantStore()
const menuOpen = ref(false)

const clubName = tenantStore.brandName
const logoUrl = tenantStore.config?.branding?.logo_url ?? null
</script>
