<template>
  <div class="dashboard-page">
    <DashboardNavbar />
    <section class="section dashboard-content">
      <div class="container">
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
import DashboardNavbar from '../components/club/DashboardNavbar.vue'
import MembershipStatusCard from '../components/club/dashboard/MembershipStatusCard.vue'
import UpcomingEventsCard from '../components/club/dashboard/UpcomingEventsCard.vue'
import ClubInfoCard from '../components/club/dashboard/ClubInfoCard.vue'
import QuickActionsCard from '../components/club/dashboard/QuickActionsCard.vue'
</script>

<style scoped>
.dashboard-page {
  min-height: 100vh;
}

.dashboard-content {
  padding-top: 4rem;
}
</style>
