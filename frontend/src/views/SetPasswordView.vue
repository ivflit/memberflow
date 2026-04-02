<template>
  <AuthLayout>
    <h1 class="auth-title">
      {{ mode === 'invite' ? 'Complete registration' : 'Set new password' }}
    </h1>

    <template v-if="!token">
      <p class="has-text-danger has-text-centered">
        This link is invalid. Request a new invitation or password reset.
      </p>
    </template>

    <template v-else-if="errorMessage">
      <p class="has-text-danger has-text-centered">
        {{ errorMessage }}
      </p>
      <p
        v-if="mode === 'reset'"
        class="auth-footer-link"
      >
        <RouterLink to="/forgot-password">
          Request a new reset link
        </RouterLink>
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

          <div class="field">
            <label class="label">Date of birth</label>
            <div class="control">
              <input
                v-model="dateOfBirth"
                class="input"
                type="date"
              >
            </div>
          </div>

          <p class="auth-section-label">
            Address <span class="has-text-grey">(optional)</span>
          </p>

          <div class="field">
            <div class="control">
              <input
                v-model="addressStreet"
                class="input"
                type="text"
                placeholder="Street address"
              >
            </div>
          </div>
          <div class="field">
            <div class="control">
              <input
                v-model="addressCity"
                class="input"
                type="text"
                placeholder="City"
              >
            </div>
          </div>
          <div class="field">
            <div class="control">
              <input
                v-model="addressPostcode"
                class="input"
                type="text"
                placeholder="Postcode"
              >
            </div>
          </div>
          <div class="field">
            <div class="control">
              <input
                v-model="addressCountry"
                class="input"
                type="text"
                placeholder="Country"
              >
            </div>
          </div>
        </template>

        <div class="field">
          <label class="label">New password</label>
          <div class="control has-icons-right">
            <input
              v-model="password"
              class="input"
              :type="showPassword ? 'text' : 'password'"
              placeholder="New password"
              required
              autocomplete="new-password"
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
          v-if="fieldError"
          class="help is-danger"
        >
          {{ fieldError }}
        </p>

        <div class="field mt-4">
          <div class="control">
            <button
              class="button is-primary is-fullwidth"
              type="submit"
              :class="{ 'is-loading': loading }"
              :disabled="loading"
            >
              Set password
            </button>
          </div>
        </div>
      </form>
    </template>
  </AuthLayout>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute, useRouter, RouterLink } from 'vue-router'
import { EyeIcon, EyeSlashIcon } from '@heroicons/vue/24/outline'
import { useAuthStore } from '../stores/auth.js'
import client from '../api/client.js'
import AuthLayout from '../components/club/AuthLayout.vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const token = route.query.token || ''
const mode = route.query.mode || 'reset'

const firstName = ref('')
const lastName = ref('')
const password = ref('')
const showPassword = ref(false)
const loading = ref(false)
const errorMessage = ref('')
const fieldError = ref('')
const dateOfBirth = ref('')
const addressStreet = ref('')
const addressCity = ref('')
const addressPostcode = ref('')
const addressCountry = ref('')

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
        ? {
            token,
            password: password.value,
            first_name: firstName.value,
            last_name: lastName.value,
            date_of_birth: dateOfBirth.value || null,
            address_street: addressStreet.value || null,
            address_city: addressCity.value || null,
            address_postcode: addressPostcode.value || null,
            address_country: addressCountry.value || null,
          }
        : { token, password: password.value }

    const { data } = await client.post(endpoint, payload)
    authStore.setTokens(data)
    router.push('/dashboard')
  } catch (err) {
    const status = err.response?.status
    const data = err.response?.data

    if (status === 410) {
      errorMessage.value = mode === 'invite'
        ? 'This invitation has expired. Ask your admin to resend.'
        : 'This reset link has expired. Request a new one.'
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
