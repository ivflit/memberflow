<template>
  <AuthLayout>
    <h1 class="auth-title">
      Forgot password
    </h1>

    <template v-if="submitted">
      <p class="has-text-grey has-text-centered">
        If that email is registered, a reset link has been sent. Check your inbox.
      </p>
      <p class="auth-footer-link">
        <RouterLink to="/login">
          Back to sign in
        </RouterLink>
      </p>
    </template>

    <template v-else>
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

        <div class="field mt-4">
          <div class="control">
            <button
              class="button is-primary is-fullwidth"
              type="submit"
              :class="{ 'is-loading': loading }"
              :disabled="loading"
            >
              Send reset link
            </button>
          </div>
        </div>
      </form>

      <p class="auth-footer-link">
        <RouterLink to="/login">
          Back to sign in
        </RouterLink>
      </p>
    </template>
  </AuthLayout>
</template>

<script setup>
import { ref } from 'vue'
import { RouterLink } from 'vue-router'
import client from '../api/client.js'
import AuthLayout from '../components/club/AuthLayout.vue'

const email = ref('')
const loading = ref(false)
const submitted = ref(false)

async function handleSubmit() {
  loading.value = true
  try {
    await client.post('/api/v1/auth/password/reset/', { email: email.value })
  } catch {
    // Always show success — no enumeration
  } finally {
    loading.value = false
    submitted.value = true
  }
}
</script>
