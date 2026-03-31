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

            <!-- Change password -->
            <div class="profile-card">
              <h2 class="profile-section-title">
                Change password
              </h2>
              <form @submit.prevent="savePassword">
                <div class="field">
                  <label class="profile-label">Current password</label>
                  <div class="control">
                    <input
                      v-model="pwForm.current_password"
                      class="input profile-input"
                      type="password"
                      autocomplete="current-password"
                      placeholder="••••••••"
                    >
                  </div>
                </div>
                <div class="field">
                  <label class="profile-label">New password</label>
                  <div class="control">
                    <input
                      v-model="pwForm.new_password"
                      class="input profile-input"
                      type="password"
                      autocomplete="new-password"
                      placeholder="••••••••"
                    >
                  </div>
                </div>
                <div class="field">
                  <label class="profile-label">Confirm new password</label>
                  <div class="control">
                    <input
                      v-model="pwForm.confirm_password"
                      class="input profile-input"
                      type="password"
                      autocomplete="new-password"
                      placeholder="••••••••"
                    >
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
import { EnvelopeIcon, BuildingOfficeIcon } from '@heroicons/vue/24/outline'
import DashboardNavbar from '../components/club/DashboardNavbar.vue'
import { getProfile, updateProfile, changePassword } from '../api/profile.js'
import { useAuthStore } from '../stores/auth.js'
import { useTenantStore } from '../stores/tenant.js'

const authStore = useAuthStore()
const tenantStore = useTenantStore()

const clubName = tenantStore.brandName
const theme = ref(localStorage.getItem('mf-theme') || 'light')

function toggleTheme() {
  theme.value = theme.value === 'dark' ? 'light' : 'dark'
  localStorage.setItem('mf-theme', theme.value)
}

const profile = ref({
  email: '',
  first_name: '',
  last_name: '',
  role: 'member',
})

const editForm = ref({ first_name: '', last_name: '' })
const pwForm = ref({ current_password: '', new_password: '', confirm_password: '' })

const savingProfile = ref(false)
const profileSuccess = ref(false)
const profileError = ref('')

const savingPw = ref(false)
const pwSuccess = ref(false)
const pwError = ref('')

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
    editForm.value = { first_name: data.first_name, last_name: data.last_name }
  } catch {
    // Fall back to auth store data if request fails
    const u = authStore.user
    if (u) {
      profile.value = { ...u }
      editForm.value = { first_name: u.first_name ?? '', last_name: u.last_name ?? '' }
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
    editForm.value = { first_name: data.first_name, last_name: data.last_name }
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
