<template>
  <section class="section">
    <div class="container">
      <div class="columns is-centered">
        <div class="column is-narrow" style="min-width: 360px;">
          <div class="box">
            <h1 class="title is-4">Sign in</h1>

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
                  />
                </div>
              </div>

              <div class="field">
                <label class="label">Password</label>
                <div class="control">
                  <input
                    v-model="password"
                    class="input"
                    type="password"
                    placeholder="Password"
                    required
                    autocomplete="current-password"
                  />
                </div>
              </div>

              <p v-if="errorMessage" class="help is-danger">{{ errorMessage }}</p>

              <div class="field">
                <div class="control">
                  <button
                    class="button is-primary is-fullwidth"
                    type="submit"
                    :disabled="loading"
                  >
                    {{ loading ? 'Signing in\u2026' : 'Sign in' }}
                  </button>
                </div>
              </div>
            </form>

            <p class="has-text-centered mt-3">
              <router-link to="/forgot-password">Forgot password?</router-link>
            </p>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth.js'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const email = ref('')
const password = ref('')
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
