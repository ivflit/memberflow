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

.membership-icon {
  background: rgba(72, 199, 142, 0.12);
  color: #48c78e;
}

.db-card-title {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--db-text-strong);
}

.db-card-body {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.skeleton-line {
  height: 0.85rem;
  border-radius: 6px;
  background: var(--db-skeleton);
  width: 100%;
  animation: shimmer 1.6s ease-in-out infinite;
}

.skeleton-line--short {
  width: 60%;
}

@keyframes shimmer {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.placeholder-msg {
  font-size: 0.8rem;
  color: var(--db-text-muted);
  margin-top: 0.5rem;
}
</style>
