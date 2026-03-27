<template>
  <section class="section">
    <div class="container">
      <div class="columns is-centered">
        <div
          class="column is-narrow"
          style="min-width: 360px;"
        >
          <div class="box">
            <h1 class="title is-4">
              {{ mode === 'invite' ? 'Complete registration' : 'Set new password' }}
            </h1>

            <template v-if="!token">
              <p class="has-text-danger">
                This link is invalid. Request a new invitation or password reset.
              </p>
            </template>

            <template v-else-if="errorMessage">
              <p class="has-text-danger">
                {{ errorMessage }}
              </p>
              <p
                v-if="mode === 'reset'"
                class="mt-3"
              >
                <router-link to="/forgot-password">
                  Request a new reset link
                </router-link>
              </p>
            </template>

            <template v-else>
              <form @submit.prevent="handleSubmit">
                <template v-if="mode === 'invite'">
                  <div class="field">
                    <label class="label">First name</label>
                    <div class="control">
                      <input
                        v-model="firstName"
                        class="input"
                        type="text"
                        placeholder="First name"
                        required
                      >
                    </div>
                  </div>

                  <div class="field">
                    <label class="label">Last name</label>
                    <div class="control">
                      <input
                        v-model="lastName"
                        class="input"
                        type="text"
                        placeholder="Last name"
                        required
                      >
                    </div>
                  </div>
                </template>

                <div class="field">
                  <label class="label">New password</label>
                  <div class="control">
                    <input
                      v-model="password"
                      class="input"
                      type="password"
                      placeholder="New password"
                      required
                      autocomplete="new-password"
                    >
                  </div>
                </div>

                <p
                  v-if="fieldError"
                  class="help is-danger"
                >
                  {{ fieldError }}
                </p>

                <div class="field">
                  <div class="control">
                    <button
                      class="button is-primary is-fullwidth"
                      type="submit"
                      :disabled="loading"
                    >
                      {{ loading ? 'Saving\u2026' : 'Set password' }}
                    </button>
                  </div>
                </div>
              </form>
            </template>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth.js'
import client from '../api/client.js'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const token = route.query.token || ''
const mode = route.query.mode || 'reset'

const firstName = ref('')
const lastName = ref('')
const password = ref('')
const loading = ref(false)
const errorMessage = ref('')
const fieldError = ref('')

async function handleSubmit() {
  loading.value = true
  fieldError.value = ''
  try {
    const endpoint =
      mode === 'invite'
        ? '/api/v1/auth/invite/accept/'
        : '/api/v1/auth/password/reset/confirm/'

    const payload =
      mode === 'invite'
        ? { token, password: password.value, first_name: firstName.value, last_name: lastName.value }
        : { token, password: password.value }

    const { data } = await client.post(endpoint, payload)
    authStore.setTokens(data)
    router.push('/dashboard')
  } catch (err) {
    const status = err.response?.status
    const data = err.response?.data

    if (status === 410) {
      if (mode === 'invite') {
        errorMessage.value = 'This invitation has expired. Ask your admin to resend.'
      } else {
        errorMessage.value = 'This reset link has expired. Request a new one.'
      }
    } else if (status === 400) {
      if (data?.detail) {
        errorMessage.value = data.detail
      } else if (data?.password) {
        const msgs = Array.isArray(data.password) ? data.password : [data.password]
        fieldError.value = msgs.join(' ')
      } else {
        errorMessage.value = 'This link has already been used.'
      }
    } else {
      fieldError.value = 'An unexpected error occurred. Please try again.'
    }
  } finally {
    loading.value = false
  }
}
</script>
