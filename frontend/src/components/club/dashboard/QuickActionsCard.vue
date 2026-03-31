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

.actions-icon {
  background: rgba(99, 102, 241, 0.12);
  color: #6366f1;
}

.db-card-title {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--db-text-strong);
}

.db-card-body {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.85rem 1rem;
  border: 1px solid var(--db-border);
  border-radius: 10px;
  text-decoration: none;
  background: transparent;
  transition: background 0.15s, border-color 0.15s;
}

.action-btn:hover {
  background: var(--db-hover-bg);
  border-color: var(--bulma-primary);
}

.action-btn-icon {
  width: 20px;
  height: 20px;
  color: var(--bulma-primary);
  flex-shrink: 0;
}

.action-btn-text {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-width: 0;
}

.action-btn-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--db-text-strong);
}

.action-btn-sub {
  font-size: 0.75rem;
  color: var(--db-text-muted);
}

.action-btn-chevron {
  width: 16px;
  height: 16px;
  color: var(--db-text-muted);
  flex-shrink: 0;
}
</style>
