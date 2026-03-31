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
import { computed } from 'vue'
import DashboardNavbar from '../components/club/DashboardNavbar.vue'
import MembershipStatusCard from '../components/club/dashboard/MembershipStatusCard.vue'
import UpcomingEventsCard from '../components/club/dashboard/UpcomingEventsCard.vue'
import ClubInfoCard from '../components/club/dashboard/ClubInfoCard.vue'
import QuickActionsCard from '../components/club/dashboard/QuickActionsCard.vue'
import { useAuthStore } from '../stores/auth.js'
import { useTenantStore } from '../stores/tenant.js'
import { useTheme } from '../composables/useTheme.js'

const authStore = useAuthStore()
const tenantStore = useTenantStore()

const firstName = computed(() => authStore.user?.first_name ?? '')
const clubName = tenantStore.brandName

const { theme, toggleTheme } = useTheme()
</script>
