<template>
  <AuthLayout>
    <h1 class="auth-title">
      Create account
    </h1>

    <template v-if="!registrationOpen">
      <p class="has-text-grey has-text-centered">
        Registration is not open. Contact your club admin.
      </p>
    </template>

    <template v-else>
      <form @submit.prevent="handleSubmit">
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
              Create account
            </button>
          </div>
        </div>
      </form>
    </template>

    <p class="auth-footer-link">
      Already have an account?
      <RouterLink to="/login">
        Sign in
      </RouterLink>
    </p>
  </AuthLayout>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import { EyeIcon, EyeSlashIcon } from '@heroicons/vue/24/outline'
import { useAuthStore } from '../stores/auth.js'
import AuthLayout from '../components/club/AuthLayout.vue'

const router = useRouter()
const authStore = useAuthStore()

const registrationOpen = computed(() => true)

const firstName = ref('')
const lastName = ref('')
const email = ref('')
const password = ref('')
const showPassword = ref(false)
const loading = ref(false)
const errorMessage = ref('')
const dateOfBirth = ref('')
const addressStreet = ref('')
const addressCity = ref('')
const addressPostcode = ref('')
const addressCountry = ref('')

async function handleSubmit() {
  loading.value = true
  errorMessage.value = ''
  try {
    await authStore.register({
      email: email.value,
      password: password.value,
      first_name: firstName.value,
      last_name: lastName.value,
      date_of_birth: dateOfBirth.value || null,
      address_street: addressStreet.value || null,
      address_city: addressCity.value || null,
      address_postcode: addressPostcode.value || null,
      address_country: addressCountry.value || null,
    })
    router.push('/dashboard')
  } catch (err) {
    const status = err.response?.status
    const data = err.response?.data
    if (status === 409) {
      errorMessage.value = 'An account with this email already exists.'
    } else if (status === 400 && data?.password) {
      const msgs = Array.isArray(data.password) ? data.password : [data.password]
      errorMessage.value = msgs.join(' ')
    } else if (status === 403) {
      errorMessage.value = 'Registration is not open. Contact your club admin.'
    } else {
      errorMessage.value = 'An unexpected error occurred. Please try again.'
    }
  } finally {
    loading.value = false
  }
}
</script>
