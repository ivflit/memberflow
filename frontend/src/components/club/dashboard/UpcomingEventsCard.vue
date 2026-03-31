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

<style scoped>
.db-card {
  background: var(--db-card-bg);
  border: 1px solid var(--db-border);
  border-radius: 14px;
  padding: 1.5rem;
  height: 100%;
  transition: background 0.2s, border-color 0.2s, box-shadow 0.2s;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.db-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

.db-card-header {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  margin-bottom: 1.25rem;
}

.db-card-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 10px;
  flex-shrink: 0;
}

.db-card-icon :deep(svg) {
  width: 18px;
  height: 18px;
}

.events-icon {
  background: rgba(72, 95, 199, 0.12);
  color: #485fc7;
}

.db-card-title {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--db-text-strong);
}

.db-card-body {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.skeleton-row {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

.skeleton-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--db-skeleton);
  flex-shrink: 0;
  animation: shimmer 1.6s ease-in-out infinite;
}

.skeleton-line {
  height: 0.8rem;
  border-radius: 6px;
  background: var(--db-skeleton);
  animation: shimmer 1.6s ease-in-out infinite;
}

@keyframes shimmer {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.placeholder-msg {
  font-size: 0.8rem;
  color: var(--db-text-muted);
  margin-top: 0.25rem;
}
</style>
