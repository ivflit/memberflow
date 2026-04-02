<template>
  <div
    class="dashboard-page"
    :data-theme="theme"
  >
    <DashboardNavbar
      :is-dark="theme === 'dark'"
      @toggle-theme="toggleTheme"
    />
    <section class="dashboard-content">
      <div class="container">
        <div class="dashboard-greeting">
          <h1 class="greeting-text">
            My Profile
          </h1>
          <p class="greeting-sub">
            View and update your account details.
          </p>
        </div>

        <div class="profile-layout">
          <!-- Avatar + info panel -->
          <div class="profile-card">
            <div class="profile-avatar-block">
              <span class="profile-avatar">{{ userInitials }}</span>
              <div>
                <p class="profile-fullname">
                  {{ fullName }}
                </p>
                <p class="profile-role">
                  {{ roleLabel }}
                </p>
              </div>
            </div>
            <hr class="profile-divider">
            <div class="profile-meta">
              <div class="profile-meta-row">
                <EnvelopeIcon class="profile-meta-icon" />
                <span class="profile-meta-value">{{ profile.email }}</span>
              </div>
              <div class="profile-meta-row">
                <BuildingOfficeIcon class="profile-meta-icon" />
                <span class="profile-meta-value">{{ clubName }}</span>
              </div>
            </div>
          </div>

          <!-- Edit + password panels -->
          <div class="profile-forms">
            <!-- Edit details -->
            <div class="profile-card">
              <h2 class="profile-section-title">
                Personal details
              </h2>
              <form @submit.prevent="saveProfile">
                <div class="field">
                  <label class="profile-label">First name</label>
                  <div class="control">
                    <input
                      v-model="editForm.first_name"
                      class="input profile-input"
                      type="text"
                      placeholder="First name"
                    >
                  </div>
                </div>
                <div class="field">
                  <label class="profile-label">Last name</label>
                  <div class="control">
                    <input
                      v-model="editForm.last_name"
                      class="input profile-input"
                      type="text"
                      placeholder="Last name"
                    >
                  </div>
                </div>
                <div class="field">
                  <label class="profile-label">Date of birth</label>
                  <div class="control">
                    <input
                      v-model="editForm.date_of_birth"
                      class="input profile-input"
                      type="date"
                    >
                  </div>
                </div>
                <div class="field">
                  <label class="profile-label">Email address</label>
                  <div class="control">
                    <input
                      class="input profile-input"
                      type="email"
                      :value="profile.email"
                      disabled
                    >
                  </div>
                  <p class="profile-help">
                    Email cannot be changed here.
                  </p>
                </div>
                <div class="profile-actions">
                  <p
                    v-if="profileSuccess"
                    class="profile-success-msg"
                  >
                    ✓ Profile updated
                  </p>
                  <p
                    v-if="profileError"
                    class="profile-error-msg"
                  >
                    {{ profileError }}
                  </p>
                  <button
                    class="button is-primary profile-save-btn"
                    type="submit"
                    :class="{ 'is-loading': savingProfile }"
                    :disabled="savingProfile"
                  >
                    Save changes
                  </button>
                </div>
              </form>
            </div>

            <!-- Address -->
            <div class="profile-card">
              <h2 class="profile-section-title">
                Address
              </h2>
              <form @submit.prevent="saveAddress">
                <div class="field">
                  <label class="profile-label">Street address</label>
                  <div class="control">
                    <input
                      v-model="addressForm.address_street"
                      class="input profile-input"
                      type="text"
                      placeholder="123 Main Street"
                    >
                  </div>
                </div>
                <div class="field">
                  <label class="profile-label">City</label>
                  <div class="control">
                    <input
                      v-model="addressForm.address_city"
                      class="input profile-input"
                      type="text"
                      placeholder="City"
                    >
                  </div>
                </div>
                <div class="field">
                  <label class="profile-label">Postcode</label>
                  <div class="control">
                    <input
                      v-model="addressForm.address_postcode"
                      class="input profile-input"
                      type="text"
                      placeholder="Postcode"
                    >
                  </div>
                </div>
                <div class="field">
                  <label class="profile-label">Country</label>
                  <div class="control">
                    <input
                      v-model="addressForm.address_country"
                      class="input profile-input"
                      type="text"
                      placeholder="Country"
                    >
                  </div>
                </div>
                <div class="profile-actions">
                  <p
                    v-if="addressSuccess"
                    class="profile-success-msg"
                  >
                    ✓ Address updated
                  </p>
                  <p
                    v-if="addressError"
                    class="profile-error-msg"
                  >
                    {{ addressError }}
                  </p>
                  <button
                    class="button is-primary profile-save-btn"
                    type="submit"
                    :class="{ 'is-loading': savingAddress }"
                    :disabled="savingAddress"
                  >
                    Save address
                  </button>
                </div>
              </form>
            </div>

            <!-- Change password -->
            <div class="profile-card">
              <h2 class="profile-section-title">
                Change password
              </h2>
              <form @submit.prevent="savePassword">
                <div class="field">
                  <label class="profile-label">Current password</label>
                  <div class="control has-icons-right">
                    <input
                      v-model="pwForm.current_password"
                      class="input profile-input"
                      :type="showCurrentPw ? 'text' : 'password'"
                      autocomplete="current-password"
                      placeholder="••••••••"
                    >
                    <span
                      class="icon is-right profile-pw-toggle"
                      @click="showCurrentPw = !showCurrentPw"
                    >
                      <EyeSlashIcon
                        v-if="showCurrentPw"
                        class="profile-pw-icon"
                      />
                      <EyeIcon
                        v-else
                        class="profile-pw-icon"
                      />
                    </span>
                  </div>
                </div>
                <div class="field">
                  <label class="profile-label">New password</label>
                  <div class="control has-icons-right">
                    <input
                      v-model="pwForm.new_password"
                      class="input profile-input"
                      :type="showNewPw ? 'text' : 'password'"
                      autocomplete="new-password"
                      placeholder="••••••••"
                    >
                    <span
                      class="icon is-right profile-pw-toggle"
                      @click="showNewPw = !showNewPw"
                    >
                      <EyeSlashIcon
                        v-if="showNewPw"
                        class="profile-pw-icon"
                      />
                      <EyeIcon
                        v-else
                        class="profile-pw-icon"
                      />
                    </span>
                  </div>
                </div>
                <div class="field">
                  <label class="profile-label">Confirm new password</label>
                  <div class="control has-icons-right">
                    <input
                      v-model="pwForm.confirm_password"
                      class="input profile-input"
                      :type="showConfirmPw ? 'text' : 'password'"
                      autocomplete="new-password"
                      placeholder="••••••••"
                    >
                    <span
                      class="icon is-right profile-pw-toggle"
                      @click="showConfirmPw = !showConfirmPw"
                    >
                      <EyeSlashIcon
                        v-if="showConfirmPw"
                        class="profile-pw-icon"
                      />
                      <EyeIcon
                        v-else
                        class="profile-pw-icon"
                      />
                    </span>
                  </div>
                </div>
                <div class="profile-actions">
                  <p
                    v-if="pwSuccess"
                    class="profile-success-msg"
                  >
                    ✓ Password updated
                  </p>
                  <p
                    v-if="pwError"
                    class="profile-error-msg"
                  >
                    {{ pwError }}
                  </p>
                  <button
                    class="button is-primary profile-save-btn"
                    type="submit"
                    :class="{ 'is-loading': savingPw }"
                    :disabled="savingPw"
                  >
                    Update password
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { EnvelopeIcon, BuildingOfficeIcon, EyeIcon, EyeSlashIcon } from '@heroicons/vue/24/outline'
import DashboardNavbar from '../components/club/DashboardNavbar.vue'
import { getProfile, updateProfile, changePassword } from '../api/profile.js'
import { useAuthStore } from '../stores/auth.js'
import { useTenantStore } from '../stores/tenant.js'
import { useTheme } from '../composables/useTheme.js'

const authStore = useAuthStore()
const tenantStore = useTenantStore()

const clubName = tenantStore.brandName
const { theme, toggleTheme } = useTheme()

const profile = ref({
  email: '',
  first_name: '',
  last_name: '',
  role: 'member',
})

const editForm = ref({ first_name: '', last_name: '', date_of_birth: '' })
const addressForm = ref({ address_street: '', address_city: '', address_postcode: '', address_country: '' })
const pwForm = ref({ current_password: '', new_password: '', confirm_password: '' })

const savingProfile = ref(false)
const profileSuccess = ref(false)
const profileError = ref('')

const savingAddress = ref(false)
const addressSuccess = ref(false)
const addressError = ref('')

const savingPw = ref(false)
const pwSuccess = ref(false)
const pwError = ref('')

const showCurrentPw = ref(false)
const showNewPw = ref(false)
const showConfirmPw = ref(false)

const userInitials = computed(() => {
  const f = profile.value.first_name
  const l = profile.value.last_name
  if (f) return (f[0] + (l ? l[0] : '')).toUpperCase()
  return profile.value.email?.[0]?.toUpperCase() ?? '?'
})

const fullName = computed(() => {
  const f = profile.value.first_name
  const l = profile.value.last_name
  if (f || l) return `${f} ${l}`.trim()
  return profile.value.email
})

const roleLabel = computed(() => {
  const map = {
    member: 'Member',
    org_staff: 'Staff',
    org_admin: 'Admin',
    platform_admin: 'Platform Admin',
  }
  return map[profile.value.role] ?? 'Member'
})

onMounted(async () => {
  try {
    const { data } = await getProfile()
    profile.value = data
    editForm.value = {
      first_name: data.first_name,
      last_name: data.last_name,
      date_of_birth: data.date_of_birth ?? '',
    }
    addressForm.value = {
      address_street: data.address_street ?? '',
      address_city: data.address_city ?? '',
      address_postcode: data.address_postcode ?? '',
      address_country: data.address_country ?? '',
    }
  } catch {
    // Fall back to auth store data if request fails
    const u = authStore.user
    if (u) {
      profile.value = { ...u }
      editForm.value = { first_name: u.first_name ?? '', last_name: u.last_name ?? '', date_of_birth: '' }
    }
  }
})

async function saveProfile() {
  profileError.value = ''
  profileSuccess.value = false
  savingProfile.value = true
  try {
    const { data } = await updateProfile(editForm.value)
    profile.value = data
    editForm.value = {
      first_name: data.first_name,
      last_name: data.last_name,
      date_of_birth: data.date_of_birth ?? '',
    }
    // Keep auth store in sync
    if (authStore.user) {
      authStore.user.first_name = data.first_name
      authStore.user.last_name = data.last_name
    }
    profileSuccess.value = true
    setTimeout(() => { profileSuccess.value = false }, 3000)
  } catch (err) {
    profileError.value = err.response?.data?.detail ?? 'Failed to update profile.'
  } finally {
    savingProfile.value = false
  }
}

async function saveAddress() {
  addressError.value = ''
  addressSuccess.value = false
  savingAddress.value = true
  try {
    const { data } = await updateProfile(addressForm.value)
    addressForm.value = {
      address_street: data.address_street ?? '',
      address_city: data.address_city ?? '',
      address_postcode: data.address_postcode ?? '',
      address_country: data.address_country ?? '',
    }
    addressSuccess.value = true
    setTimeout(() => { addressSuccess.value = false }, 3000)
  } catch (err) {
    addressError.value = err.response?.data?.detail ?? 'Failed to update address.'
  } finally {
    savingAddress.value = false
  }
}

async function savePassword() {
  pwError.value = ''
  pwSuccess.value = false
  if (pwForm.value.new_password !== pwForm.value.confirm_password) {
    pwError.value = 'New passwords do not match.'
    return
  }
  savingPw.value = true
  try {
    await changePassword({
      current_password: pwForm.value.current_password,
      new_password: pwForm.value.new_password,
    })
    pwForm.value = { current_password: '', new_password: '', confirm_password: '' }
    pwSuccess.value = true
    setTimeout(() => { pwSuccess.value = false }, 3000)
  } catch (err) {
    const data = err.response?.data
    if (data?.detail) pwError.value = data.detail
    else if (data?.new_password) pwError.value = data.new_password.join(' ')
    else pwError.value = 'Failed to update password.'
  } finally {
    savingPw.value = false
  }
}
</script>
