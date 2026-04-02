<template>
  <nav
    class="navbar is-fixed-top club-navbar"
    role="navigation"
    aria-label="main navigation"
  >
    <div class="container">
      <div class="navbar-brand">
        <RouterLink
          class="navbar-item club-brand"
          :to="isAuthenticated ? '/dashboard' : '/'"
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
        <!-- Authenticated nav links -->
        <div
          v-if="isAuthenticated"
          class="navbar-start"
        >
          <RouterLink
            class="navbar-item cn-nav-link"
            :class="{ 'is-active': route.path === '/dashboard' }"
            to="/dashboard"
          >
            Dashboard
          </RouterLink>
          <RouterLink
            class="navbar-item cn-nav-link"
            :class="{ 'is-active': route.path === '/events' }"
            to="/events"
          >
            Events
          </RouterLink>
          <RouterLink
            class="navbar-item cn-nav-link"
            :class="{ 'is-active': route.path === '/profile' }"
            to="/profile"
          >
            Profile
          </RouterLink>
        </div>

        <!-- Public nav links -->
        <div
          v-else
          class="navbar-start"
        >
          <RouterLink
            class="navbar-item cn-nav-link"
            to="/events"
          >
            Events
          </RouterLink>
        </div>

        <div class="navbar-end">
          <!-- Theme toggle -->
          <div class="navbar-item">
            <button
              class="button is-ghost cn-icon-btn"
              :aria-label="isDark ? 'Switch to light mode' : 'Switch to dark mode'"
              @click.stop="$emit('toggle-theme')"
            >
              <SunIcon
                v-if="isDark"
                class="cn-nav-icon"
              />
              <MoonIcon
                v-else
                class="cn-nav-icon"
              />
            </button>
          </div>

          <!-- Authenticated: bell + avatar -->
          <template v-if="isAuthenticated">
            <div
              ref="bellRef"
              class="navbar-item cn-icon-wrapper"
            >
              <button
                class="button is-ghost cn-icon-btn"
                aria-label="Notifications"
                @click.stop="toggleDropdown('bell')"
              >
                <BellIcon class="cn-nav-icon" />
              </button>
              <Transition name="cn-dropdown-fade">
                <div
                  v-if="openDropdown === 'bell'"
                  class="cn-dropdown-panel"
                >
                  <div class="cn-dropdown-item cn-dropdown-item--muted">
                    <BellIcon class="cn-dropdown-icon" />
                    <span>No notifications yet</span>
                  </div>
                </div>
              </Transition>
            </div>

            <div
              ref="avatarRef"
              class="navbar-item cn-icon-wrapper"
            >
              <button
                class="button is-ghost cn-icon-btn"
                aria-label="User menu"
                @click.stop="toggleDropdown('user')"
              >
                <span class="cn-avatar">{{ userInitials }}</span>
              </button>
              <Transition name="cn-dropdown-fade">
                <div
                  v-if="openDropdown === 'user'"
                  class="cn-dropdown-panel cn-avatar-panel"
                >
                  <div class="cn-dropdown-user-info">
                    <span class="cn-avatar cn-avatar--lg">{{ userInitials }}</span>
                    <span class="cn-user-email">{{ authStore.user?.email }}</span>
                  </div>
                  <hr class="cn-dropdown-divider">
                  <RouterLink
                    class="cn-dropdown-item"
                    to="/profile"
                    @click="openDropdown = null"
                  >
                    Profile
                  </RouterLink>
                  <hr class="cn-dropdown-divider">
                  <a
                    class="cn-dropdown-item cn-dropdown-item--danger"
                    href="#"
                    @click.prevent="handleSignOut"
                  >
                    Sign out
                  </a>
                </div>
              </Transition>
            </div>
          </template>

          <!-- Guest: login + join -->
          <div
            v-else
            class="navbar-item"
          >
            <div class="buttons">
              <RouterLink
                class="button is-light cn-login-btn"
                to="/login"
              >
                Log in
              </RouterLink>
              <RouterLink
                class="button is-primary cn-join-btn"
                to="/register"
              >
                Join Now
              </RouterLink>
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
import { SunIcon, MoonIcon, BellIcon } from '@heroicons/vue/24/outline'
import { useTenantStore } from '../../stores/tenant.js'
import { useAuthStore } from '../../stores/auth.js'

defineProps({
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

const clubName = tenantStore.brandName
const logoUrl = tenantStore.config?.branding?.logo_url ?? null

const menuOpen = ref(false)
const openDropdown = ref(null)
const bellRef = ref(null)
const avatarRef = ref(null)

const isAuthenticated = computed(() => authStore.isAuthenticated)

const userInitials = computed(() => {
  const user = authStore.user
  if (!user) return '?'
  if (user.first_name) {
    const first = user.first_name[0].toUpperCase()
    const last = user.last_name ? user.last_name[0].toUpperCase() : ''
    return first + last
  }
  return user.email?.[0]?.toUpperCase() ?? '?'
})

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
