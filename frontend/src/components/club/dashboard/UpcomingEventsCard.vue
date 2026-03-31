<template>
  <div class="db-card">
    <div class="db-card-header">
      <span class="db-card-icon events-icon">
        <CalendarDaysIcon />
      </span>
      <h2 class="db-card-title">
        Upcoming Events
      </h2>
    </div>
    <div class="db-card-body">
      <div
        v-for="i in 3"
        :key="i"
        class="skeleton-row"
      >
        <div class="skeleton-dot" />
        <div
          class="skeleton-line"
          :style="{ width: i === 2 ? '55%' : '80%' }"
        />
      </div>
      <p class="placeholder-msg">
        Events will appear here when available
      </p>
    </div>
  </div>
</template>

<script setup>
import { CalendarDaysIcon } from '@heroicons/vue/24/outline'
</script>

