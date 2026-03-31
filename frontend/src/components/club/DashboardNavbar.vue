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
            class="navbar-item nav-link"
            :class="{ 'is-active': route.path === '/dashboard' }"
            to="/dashboard"
          >
            Dashboard
          </RouterLink>
          <RouterLink
            class="navbar-item nav-link"
            to="/events"
          >
            Events
          </RouterLink>
          <RouterLink
            class="navbar-item nav-link"
            to="/profile"
          >
            Profile
          </RouterLink>
        </div>

        <div class="navbar-end">
          <!-- Theme toggle -->
          <div class="navbar-item">
            <button
              class="button is-ghost theme-btn"
              :aria-label="isDark ? 'Switch to light mode' : 'Switch to dark mode'"
              @click.stop="$emit('toggle-theme')"
            >
              <SunIcon
                v-if="isDark"
                class="theme-icon"
              />
              <MoonIcon
                v-else
                class="theme-icon"
              />
            </button>
          </div>

          <!-- Bell -->
          <div
            ref="bellRef"
            class="navbar-item icon-wrapper"
          >
            <button
              class="button is-ghost icon-btn"
              aria-label="Notifications"
              @click.stop="toggleDropdown('bell')"
            >
              <BellIcon class="nav-icon" />
            </button>
            <Transition name="dropdown-fade">
              <div
                v-if="openDropdown === 'bell'"
                class="dropdown-panel"
              >
                <div class="dropdown-item has-text-grey-light">
                  <BellIcon class="dropdown-icon" />
                  <span>No notifications yet</span>
                </div>
              </div>
            </Transition>
          </div>

          <!-- Avatar -->
          <div
            ref="avatarRef"
            class="navbar-item icon-wrapper"
          >
            <button
              class="button is-ghost icon-btn"
              aria-label="User menu"
              @click.stop="toggleDropdown('user')"
            >
              <span class="avatar-circle">{{ userInitials }}</span>
            </button>
            <Transition name="dropdown-fade">
              <div
                v-if="openDropdown === 'user'"
                class="dropdown-panel avatar-panel"
              >
                <div class="dropdown-user-info">
                  <span class="avatar-circle avatar-circle--lg">{{ userInitials }}</span>
                  <span class="user-email">{{ authStore.user?.email }}</span>
                </div>
                <hr class="dropdown-divider">
                <RouterLink
                  class="dropdown-item"
                  to="/profile"
                  @click="openDropdown = null"
                >
                  Profile
                </RouterLink>
                <hr class="dropdown-divider">
                <a
                  class="dropdown-item dropdown-item--danger"
                  href="#"
                  @click.prevent="handleSignOut"
                >
                  Sign out
                </a>
              </div>
            </Transition>
          </div>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute, RouterLink } from 'vue-router'
import { BellIcon, MoonIcon, SunIcon } from '@heroicons/vue/24/outline'
import { useTenantStore } from '../../stores/tenant.js'
import { useAuthStore } from '../../stores/auth.js'

const props = defineProps({
  isDark: {
    type: Boolean,
    default: false,
  },
})

defineEmits(['toggle-theme'])

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
  if (user.email) return user.email[0].toUpperCase()
  return '?'
})

function toggleMenu() {
  menuOpen.value = !menuOpen.value
  if (!menuOpen.value) openDropdown.value = null
}

function toggleDropdown(name) {
  openDropdown.value = openDropdown.value === name ? null : name
}

async function handleSignOut() {
  openDropdown.value = null
  await authStore.logout()
  router.push('/login')
}

function handleOutsideClick() {
  openDropdown.value = null
}

onMounted(() => document.addEventListener('click', handleOutsideClick))
onUnmounted(() => document.removeEventListener('click', handleOutsideClick))
</script>

<style scoped>
/* ── Navbar shell ── */
.dashboard-navbar {
  background: var(--db-navbar-bg);
  box-shadow: 0 1px 0 var(--db-border);
  padding: 0.25rem 0;
  transition: background 0.2s, box-shadow 0.2s;
}

.club-brand {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

.club-logo {
  height: 34px;
  width: auto;
  object-fit: contain;
}

.club-name {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--db-text-strong);
  letter-spacing: -0.3px;
}

/* ── Nav links ── */
.nav-link {
  color: var(--db-text-muted);
  font-size: 0.9rem;
  font-weight: 500;
  border-bottom: 2px solid transparent;
  transition: color 0.15s, border-color 0.15s;
}

.nav-link:hover {
  color: var(--db-text-strong);
  background: transparent;
}

.nav-link.is-active {
  color: var(--bulma-primary);
  border-bottom-color: var(--bulma-primary);
  font-weight: 600;
  background: transparent;
}

/* ── Burger ── */
.navbar-burger span {
  background-color: var(--db-text-muted);
}

/* ── Icon buttons ── */
.icon-wrapper {
  position: relative;
}

.icon-btn,
.theme-btn {
  background: none !important;
  border: none !important;
  box-shadow: none !important;
  text-decoration: none !important;
  cursor: pointer;
  padding: 0.4rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  transition: background 0.15s;
}

.icon-btn:hover,
.icon-btn:focus,
.icon-btn:active {
  text-decoration: none !important;
}

/* Fade transition for dropdowns */
.dropdown-fade-enter-active,
.dropdown-fade-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}

.dropdown-fade-enter-from,
.dropdown-fade-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}

.icon-btn:hover,
.theme-btn:hover {
  background: var(--db-hover-bg) !important;
}

.nav-icon,
.theme-icon {
  width: 20px;
  height: 20px;
  color: var(--db-text-muted);
}

/* ── Avatar circle ── */
.avatar-circle {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--bulma-primary);
  color: #ffffff;
  font-size: 0.8rem;
  font-weight: 700;
  letter-spacing: 0.5px;
  flex-shrink: 0;
}

.avatar-circle--lg {
  width: 40px;
  height: 40px;
  font-size: 1rem;
}

/* ── Dropdown panel ── */
.dropdown-panel {
  position: absolute;
  top: calc(100% + 6px);
  right: 0;
  min-width: 200px;
  background: var(--db-card-bg);
  border: 1px solid var(--db-border);
  border-radius: 10px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  z-index: 9999;
  overflow: hidden;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.65rem 1rem;
  font-size: 0.9rem;
  color: var(--db-text);
  text-decoration: none;
  transition: background 0.12s;
  cursor: pointer;
}

.dropdown-item:hover {
  background: var(--db-hover-bg);
}

.dropdown-item--danger {
  color: var(--bulma-danger, #f14668);
}

.dropdown-icon {
  width: 16px;
  height: 16px;
  color: var(--db-text-muted);
  flex-shrink: 0;
}

.dropdown-divider {
  margin: 0;
  border: none;
  border-top: 1px solid var(--db-border);
}

.dropdown-user-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.85rem 1rem;
}

.user-email {
  font-size: 0.8rem;
  color: var(--db-text-muted);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 140px;
}

/* Avatar panel is a bit wider */
.avatar-panel {
  min-width: 220px;
}
</style>
