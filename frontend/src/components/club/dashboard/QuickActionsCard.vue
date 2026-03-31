<template>
  <div class="db-card">
    <div class="db-card-header">
      <span class="db-card-icon actions-icon">
        <BoltIcon />
      </span>
      <h2 class="db-card-title">
        Quick Actions
      </h2>
    </div>
    <div class="db-card-body">
      <RouterLink
        class="action-btn"
        to="/membership"
      >
        <CreditCardIcon class="action-btn-icon" />
        <div class="action-btn-text">
          <span class="action-btn-label">Renew Membership</span>
          <span class="action-btn-sub">Keep your membership active</span>
        </div>
        <ChevronRightIcon class="action-btn-chevron" />
      </RouterLink>
      <RouterLink
        class="action-btn"
        to="/profile"
      >
        <UserCircleIcon class="action-btn-icon" />
        <div class="action-btn-text">
          <span class="action-btn-label">Update Profile</span>
          <span class="action-btn-sub">Edit your details</span>
        </div>
        <ChevronRightIcon class="action-btn-chevron" />
      </RouterLink>
    </div>
  </div>
</template>

<script setup>
import { RouterLink } from 'vue-router'
import { BoltIcon, CreditCardIcon, UserCircleIcon, ChevronRightIcon } from '@heroicons/vue/24/outline'
</script>

