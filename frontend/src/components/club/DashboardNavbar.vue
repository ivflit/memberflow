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

