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
              Forgot password
            </h1>

            <template v-if="submitted">
              <p class="has-text-grey">
                If that email is registered, a reset link has been sent. Check your inbox.
              </p>
              <p class="mt-3">
                <router-link to="/login">
                  Back to sign in
                </router-link>
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

                <div class="field">
                  <div class="control">
                    <button
                      class="button is-primary is-fullwidth"
                      type="submit"
                      :disabled="loading"
                    >
                      {{ loading ? 'Sending\u2026' : 'Send reset link' }}
                    </button>
                  </div>
                </div>
              </form>

              <p class="mt-3 has-text-centered">
                <router-link to="/login">
                  Back to sign in
                </router-link>
              </p>
            </template>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import client from '../api/client.js'

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
