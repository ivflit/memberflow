<template>
  <AuthLayout>
    <h1 class="auth-title">
      Sign in
    </h1>

    <form @submit.prevent="handleSubmit">
      <div class="field">
        <label class="label">Email</label>
        <div class="control">
          <input
            v-model="email"
            class="input"
            type="email"
            placeholder="you@example.com"
            required
            autocomplete="email"
          >
        </div>
      </div>

      <div class="field">
        <label class="label">Password</label>
        <div class="control has-icons-right">
          <input
            v-model="password"
            class="input"
            :type="showPassword ? 'text' : 'password'"
            placeholder="Password"
            required
            autocomplete="current-password"
          >
          <span
            class="icon is-right pw-toggle"
            @click="showPassword = !showPassword"
          >
            <EyeSlashIcon
              v-if="showPassword"
              class="pw-icon"
            />
            <EyeIcon
              v-else
              class="pw-icon"
            />
          </span>
        </div>
      </div>

      <p
        v-if="errorMessage"
        class="help is-danger"
      >
        {{ errorMessage }}
      </p>

      <div class="field mt-4">
        <div class="control">
          <button
            class="button is-primary is-fullwidth"
            type="submit"
            :class="{ 'is-loading': loading }"
            :disabled="loading"
          >
            Sign in
          </button>
        </div>
      </div>
    </form>

    <p class="auth-footer-link">
      <RouterLink to="/forgot-password">
        Forgot password?
      </RouterLink>
    </p>
    <p class="auth-footer-link">
      Don't have an account?
      <RouterLink to="/register">
        Register
      </RouterLink>
    </p>
  </AuthLayout>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, useRoute, RouterLink } from 'vue-router'
import { EyeIcon, EyeSlashIcon } from '@heroicons/vue/24/outline'
import { useAuthStore } from '../stores/auth.js'
import AuthLayout from '../components/club/AuthLayout.vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const email = ref('')
const password = ref('')
const showPassword = ref(false)
const loading = ref(false)
const errorMessage = ref('')

async function handleSubmit() {
  loading.value = true
  errorMessage.value = ''
  try {
    await authStore.login(email.value, password.value)
    const next = route.query.next || '/dashboard'
    router.push(next)
  } catch (err) {
    const status = err.response?.status
    if (status === 401) {
      errorMessage.value = 'Invalid email or password.'
    } else if (status === 403) {
      errorMessage.value = 'Your account has been deactivated. Contact your admin.'
    } else {
      errorMessage.value = 'An unexpected error occurred. Please try again.'
    }
  } finally {
    loading.value = false
  }
}
</script>
