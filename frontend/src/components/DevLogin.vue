<template>
  <div
    v-if="isDev"
    class="dev-login"
  >
    <div
      class="dev-login-panel"
      :class="{ 'is-open': open }"
    >
      <div
        v-if="open"
        class="dev-login-buttons"
      >
        <button
          v-for="u in devUsers"
          :key="u.role"
          class="dev-login-btn"
          :class="{
            'is-active': currentRole === u.role,
            'is-loading-btn': loadingRole === u.role,
          }"
          :disabled="!!loadingRole"
          @click="loginAs(u)"
        >
          <span
            class="dev-role-dot"
            :class="`role-${u.role}`"
          />
          {{ u.label }}
        </button>

        <button
          v-if="isAuthenticated"
          class="dev-login-btn dev-logout-btn"
          :disabled="!!loadingRole"
          @click="doLogout"
        >
          ↩ Sign out
        </button>
      </div>

      <button
        class="dev-login-toggle"
        :title="open ? 'Close dev login' : 'Dev quick login'"
        @click="open = !open"
      >
        <span class="dev-badge">DEV</span>
        <span class="dev-label">{{ currentRole ?? 'Login' }}</span>
        <span class="dev-chevron">{{ open ? '▾' : '▸' }}</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth.js'

const isDev = import.meta.env.DEV

const authStore = useAuthStore()
const router = useRouter()

const open = ref(false)
const loadingRole = ref(null)

const isAuthenticated = computed(() => authStore.isAuthenticated)
const currentRole = computed(() => authStore.user?.role ?? null)

const devUsers = [
  { label: 'Member', role: 'member', email: 'member@dev.local', password: 'devpass123' },
  { label: 'Staff', role: 'org_staff', email: 'staff@dev.local', password: 'devpass123' },
  { label: 'Admin', role: 'org_admin', email: 'admin@dev.local', password: 'devpass123' },
]

async function loginAs(user) {
  if (loadingRole.value) return
  loadingRole.value = user.role
  try {
    if (authStore.isAuthenticated) await authStore.logout()
    await authStore.login(user.email, user.password)
    open.value = false
    router.push('/dashboard')
  } catch {
    // credentials not seeded yet — silently ignore
  } finally {
    loadingRole.value = null
  }
}

async function doLogout() {
  await authStore.logout()
  router.push('/login')
}
</script>
