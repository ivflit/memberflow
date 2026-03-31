<template>
  <nav
    class="navbar is-fixed-top dashboard-navbar"
    role="navigation"
    aria-label="main navigation"
  >
    <div class="container">
      <div class="navbar-brand">
        <RouterLink
          class="navbar-item club-brand"
          to="/dashboard"
        >
          <img
            v-if="logoUrl"
            :src="logoUrl"
            :alt="clubName"
            class="club-logo"
          >
          <span class="club-name">{{ clubName }}</span>
        </RouterLink>

        <a
          role="button"
          class="navbar-burger"
          :class="{ 'is-active': menuOpen }"
          aria-label="menu"
          :aria-expanded="menuOpen"
          @click="toggleMenu"
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
        <div class="navbar-start">
          <RouterLink
            class="navbar-item"
            :class="{ 'is-active': route.path === '/dashboard' }"
            to="/dashboard"
          >
            Dashboard
          </RouterLink>
          <RouterLink
            class="navbar-item"
            to="/events"
          >
            Events
          </RouterLink>
          <RouterLink
            class="navbar-item"
            to="/profile"
          >
            Profile
          </RouterLink>
        </div>

        <div class="navbar-end">
          <!-- Bell icon -->
          <div
            ref="bellRef"
            class="navbar-item bell-wrapper"
          >
            <button
              class="button is-ghost bell-btn"
              aria-label="Notifications"
              @click="toggleDropdown('bell')"
            >
              <BellIcon class="icon-bell" />
            </button>
            <div
              v-show="openDropdown === 'bell'"
              class="navbar-dropdown bell-dropdown"
            >
              <div class="navbar-item has-text-grey">
                No notifications yet
              </div>
            </div>
          </div>

          <!-- User avatar -->
          <div
            ref="avatarRef"
            class="navbar-item avatar-wrapper"
          >
            <button
              class="button is-ghost avatar-btn"
              aria-label="User menu"
              @click="toggleDropdown('user')"
            >
              <span class="avatar-circle">{{ userInitials }}</span>
            </button>
            <div
              v-show="openDropdown === 'user'"
              class="navbar-dropdown avatar-dropdown"
            >
              <RouterLink
                class="navbar-item"
                to="/profile"
              >
                Profile
              </RouterLink>
              <hr class="navbar-divider">
              <a
                class="navbar-item"
                href="#"
                @click.prevent="handleSignOut"
              >
                Sign out
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute, RouterLink } from 'vue-router'
import { BellIcon } from '@heroicons/vue/24/outline'
import { useTenantStore } from '../../stores/tenant.js'
import { useAuthStore } from '../../stores/auth.js'

const tenantStore = useTenantStore()
const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()

const menuOpen = ref(false)
const openDropdown = ref(null)
const bellRef = ref(null)
const avatarRef = ref(null)

const clubName = tenantStore.brandName
const logoUrl = tenantStore.config?.branding?.logo_url ?? null

const userInitials = computed(() => {
  const user = authStore.user
  if (!user) return '?'
  if (user.first_name) {
    const first = user.first_name[0].toUpperCase()
    const last = user.last_name ? user.last_name[0].toUpperCase() : ''
    return first + last
  }
  if (user.email) {
    return user.email[0].toUpperCase()
  }
  return '?'
})

function toggleMenu() {
  menuOpen.value = !menuOpen.value
  if (!menuOpen.value) {
    openDropdown.value = null
  }
}

function toggleDropdown(name) {
  openDropdown.value = openDropdown.value === name ? null : name
}

async function handleSignOut() {
  openDropdown.value = null
  await authStore.logout()
  router.push('/login')
}

function handleOutsideClick(event) {
  const clickedBell = bellRef.value && bellRef.value.contains(event.target)
  const clickedAvatar = avatarRef.value && avatarRef.value.contains(event.target)
  if (!clickedBell && !clickedAvatar) {
    openDropdown.value = null
  }
}

onMounted(() => {
  document.addEventListener('click', handleOutsideClick)
})

onUnmounted(() => {
  document.removeEventListener('click', handleOutsideClick)
})
</script>

<style scoped>
.dashboard-navbar {
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

.navbar-burger span {
  background-color: var(--mf-navy, #1b2a4a);
}

.navbar-item.is-active {
  color: var(--bulma-primary);
  font-weight: 600;
}

/* Bell icon */
.bell-wrapper,
.avatar-wrapper {
  position: relative;
}

.bell-btn,
.avatar-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.4rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.icon-bell {
  width: 22px;
  height: 22px;
  color: var(--mf-navy, #1b2a4a);
}

/* Avatar circle */
.avatar-circle {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background: var(--bulma-primary);
  color: #ffffff;
  font-size: 0.85rem;
  font-weight: 700;
  letter-spacing: 0.5px;
  cursor: pointer;
  user-select: none;
}

/* Dropdowns */
.bell-dropdown,
.avatar-dropdown {
  position: absolute;
  top: calc(100% + 4px);
  right: 0;
  min-width: 180px;
  background: #ffffff;
  border: 1px solid #dbdbdb;
  border-radius: 6px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  z-index: 9999;
}

.navbar-divider {
  margin: 0.25rem 0;
}
</style>
