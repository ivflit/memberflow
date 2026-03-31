<template>
  <div class="db-card">
    <div class="db-card-header">
      <span class="db-card-icon membership-icon">
        <IdentificationIcon />
      </span>
      <h2 class="db-card-title">
        Membership Status
      </h2>
    </div>
    <div class="db-card-body">
      <div class="skeleton-line" />
      <div class="skeleton-line skeleton-line--short" />
      <p class="placeholder-msg">
        Your membership details will appear here
      </p>
    </div>
  </div>
</template>

<script setup>
import { IdentificationIcon } from '@heroicons/vue/24/outline'
</script>

