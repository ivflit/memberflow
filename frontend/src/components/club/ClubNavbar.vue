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
import { useTenantStore } from '../../stores/tenant.js'

const tenantStore = useTenantStore()
const menuOpen = ref(false)

const clubName = tenantStore.brandName
const logoUrl = tenantStore.config?.branding?.logo_url ?? null
</script>

<style scoped>
.club-navbar {
  background: #ffffff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  padding: 0.25rem 0;
}

.club-brand {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

.club-logo {
  height: 36px;
  width: auto;
  object-fit: contain;
}

.club-name {
  font-size: 1.15rem;
  font-weight: 700;
  color: var(--mf-navy, #1b2a4a);
  letter-spacing: -0.3px;
}

.login-btn {
  font-weight: 600;
  border-color: var(--bulma-primary);
  color: var(--bulma-primary);
}

.login-btn:hover {
  background: var(--bulma-primary);
  color: #ffffff;
}

.join-btn {
  font-weight: 700;
}

.navbar-burger span {
  background-color: var(--mf-navy, #1b2a4a);
}
</style>
