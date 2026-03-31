<template>
  <div class="card">
    <div class="card-header">
      <p class="card-header-title">
        Quick Actions
      </p>
    </div>
    <div class="card-content">
      <div class="buttons">
        <RouterLink
          class="button is-primary"
          to="/membership"
        >
          Renew Membership
        </RouterLink>
        <RouterLink
          class="button is-primary"
          to="/profile"
        >
          Update Profile
        </RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup>
import { RouterLink } from 'vue-router'
</script>
