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

<style scoped>
/* ── Theme tokens (mirrors DashboardView) ── */
.dashboard-page[data-theme="light"] {
  --db-bg: #f5f7fa;
  --db-navbar-bg: #ffffff;
  --db-card-bg: #ffffff;
  --db-border: #e8ecf0;
  --db-text: #2d3748;
  --db-text-strong: #1a202c;
  --db-text-muted: #718096;
  --db-hover-bg: #f0f4f8;
  --db-skeleton: #e2e8f0;
  --db-greeting-text: #1a202c;
}

.dashboard-page[data-theme="dark"] {
  --db-bg: #0f1117;
  --db-navbar-bg: #1a1d27;
  --db-card-bg: #1e2130;
  --db-border: #2d3148;
  --db-text: #cbd5e0;
  --db-text-strong: #f7fafc;
  --db-text-muted: #718096;
  --db-hover-bg: #252838;
  --db-skeleton: #2d3148;
  --db-greeting-text: #f7fafc;
}

.dashboard-page {
  min-height: 100vh;
  background: var(--db-bg);
  transition: background 0.2s;
}

.dashboard-content {
  padding-top: 5rem;
  padding-bottom: 3rem;
  padding-left: 1rem;
  padding-right: 1rem;
}

.dashboard-greeting {
  margin-bottom: 2rem;
}

.greeting-text {
  font-size: 1.6rem;
  font-weight: 700;
  color: var(--db-greeting-text);
  line-height: 1.2;
}

.greeting-sub {
  color: var(--db-text-muted);
  margin-top: 0.25rem;
  font-size: 0.95rem;
}

/* ── Layout ── */
.profile-layout {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 1.5rem;
  align-items: start;
}

@media (max-width: 768px) {
  .profile-layout {
    grid-template-columns: 1fr;
  }
}

.profile-forms {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* ── Card ── */
.profile-card {
  background: var(--db-card-bg);
  border: 1px solid var(--db-border);
  border-radius: 14px;
  padding: 1.75rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
  transition: background 0.2s, border-color 0.2s;
}

/* ── Avatar block ── */
.profile-avatar-block {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.profile-avatar {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: var(--bulma-primary);
  color: #ffffff;
  font-size: 1.3rem;
  font-weight: 700;
  flex-shrink: 0;
}

.profile-fullname {
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--db-text-strong);
}

.profile-role {
  font-size: 0.8rem;
  color: var(--db-text-muted);
  margin-top: 0.1rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.profile-divider {
  border: none;
  border-top: 1px solid var(--db-border);
  margin: 1.25rem 0;
}

/* ── Meta rows ── */
.profile-meta {
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
}

.profile-meta-row {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

.profile-meta-icon {
  width: 16px;
  height: 16px;
  color: var(--db-text-muted);
  flex-shrink: 0;
}

.profile-meta-value {
  font-size: 0.875rem;
  color: var(--db-text);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* ── Section title ── */
.profile-section-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--db-text-strong);
  margin-bottom: 1.25rem;
}

/* ── Form inputs ── */
.profile-label {
  display: block;
  font-size: 0.825rem;
  font-weight: 600;
  color: var(--db-text-muted);
  margin-bottom: 0.35rem;
  text-transform: uppercase;
  letter-spacing: 0.4px;
}

.profile-input {
  background: var(--db-bg) !important;
  border-color: var(--db-border) !important;
  color: var(--db-text-strong) !important;
  border-radius: 8px !important;
  transition: border-color 0.15s, box-shadow 0.15s;
}

.profile-input:focus {
  border-color: var(--bulma-primary) !important;
  box-shadow: 0 0 0 2px rgba(var(--bulma-primary-rgb, 72, 95, 199), 0.15) !important;
}

.profile-input:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.profile-help {
  font-size: 0.775rem;
  color: var(--db-text-muted);
  margin-top: 0.3rem;
}

/* ── Actions row ── */
.profile-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1.25rem;
}

.profile-save-btn {
  border-radius: 8px;
  font-weight: 600;
}

.profile-success-msg {
  font-size: 0.875rem;
  color: #48c78e;
  font-weight: 500;
}

.profile-error-msg {
  font-size: 0.875rem;
  color: var(--bulma-danger, #f14668);
  font-weight: 500;
}
</style>
