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
            Welcome back{{ firstName ? ', ' + firstName : '' }} 👋
          </h1>
          <p class="greeting-sub">
            Here's what's happening at {{ clubName }}.
          </p>
        </div>
        <div class="columns is-multiline">
          <div class="column is-half-tablet is-half-desktop is-full-mobile">
            <MembershipStatusCard />
          </div>
          <div class="column is-half-tablet is-half-desktop is-full-mobile">
            <UpcomingEventsCard />
          </div>
          <div class="column is-half-tablet is-half-desktop is-full-mobile">
            <ClubInfoCard />
          </div>
          <div class="column is-half-tablet is-half-desktop is-full-mobile">
            <QuickActionsCard />
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import DashboardNavbar from '../components/club/DashboardNavbar.vue'
import MembershipStatusCard from '../components/club/dashboard/MembershipStatusCard.vue'
import UpcomingEventsCard from '../components/club/dashboard/UpcomingEventsCard.vue'
import ClubInfoCard from '../components/club/dashboard/ClubInfoCard.vue'
import QuickActionsCard from '../components/club/dashboard/QuickActionsCard.vue'
import { useAuthStore } from '../stores/auth.js'
import { useTenantStore } from '../stores/tenant.js'

const authStore = useAuthStore()
const tenantStore = useTenantStore()

const firstName = computed(() => authStore.user?.first_name ?? '')
const clubName = tenantStore.brandName

const theme = ref(localStorage.getItem('mf-theme') || 'light')

function toggleTheme() {
  theme.value = theme.value === 'dark' ? 'light' : 'dark'
  localStorage.setItem('mf-theme', theme.value)
}
</script>

<style scoped>
/* ── Theme tokens ── */
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

/* ── Page layout ── */
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

/* ── Greeting ── */
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

/* ── Card column gaps ── */
.columns {
  margin: 0 -0.75rem;
}

.column {
  padding: 0.75rem;
}
</style>
