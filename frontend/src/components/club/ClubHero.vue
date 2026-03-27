<template>
  <section class="hero is-fullheight club-hero">
    <div class="hero-body">
      <div class="container has-text-centered">
        <div data-aos="fade-up">
          <!-- Logo or initials avatar -->
          <div class="club-logo-wrap">
            <img
              v-if="logoUrl"
              :src="logoUrl"
              :alt="clubName"
              class="club-hero-logo"
            >
            <div
              v-else
              class="club-initials-avatar"
              aria-hidden="true"
            >
              {{ initials }}
            </div>
          </div>

          <h1 class="title is-1 club-hero-title">
            {{ clubName }}
          </h1>
          <p class="subtitle is-4 club-hero-tagline">
            Welcome to {{ clubName }}
          </p>

          <a
            class="button is-large club-join-btn"
            href="/register"
          >
            Join Now
          </a>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { useTenantStore } from '../../stores/tenant.js'

const tenantStore = useTenantStore()

const clubName = tenantStore.brandName
const logoUrl = tenantStore.config?.branding?.logo_url ?? null

const initials = computed(() => {
  return clubName
    .split(' ')
    .slice(0, 2)
    .map((w) => w[0]?.toUpperCase() ?? '')
    .join('')
})
</script>

<style scoped>
.club-hero {
  background: var(--bulma-primary, #1b2a4a);
  position: relative;
}

.club-hero::after {
  content: '';
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  pointer-events: none;
}

.hero-body {
  position: relative;
  z-index: 1;
}

.club-logo-wrap {
  margin-bottom: 1.5rem;
  display: flex;
  justify-content: center;
}

.club-hero-logo {
  height: 120px;
  width: auto;
  object-fit: contain;
  border-radius: 12px;
}

.club-initials-avatar {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.15);
  border: 3px solid rgba(255, 255, 255, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2.5rem;
  font-weight: 800;
  color: #ffffff;
  letter-spacing: 2px;
}

.club-hero-title {
  color: #ffffff;
  font-size: 3rem;
  font-weight: 800;
  line-height: 1.15;
  margin-bottom: 0.75rem;
}

.club-hero-tagline {
  color: rgba(255, 255, 255, 0.85);
  margin-bottom: 2.5rem;
}

.club-join-btn {
  background: #ffffff;
  color: var(--bulma-primary, #1b2a4a);
  font-weight: 700;
  padding: 1rem 2.5rem;
  border-radius: 8px;
  border: none;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.club-join-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25);
  color: var(--bulma-primary, #1b2a4a);
}

@media (max-width: 768px) {
  .club-hero-title {
    font-size: 2rem;
  }

  .club-hero-logo {
    height: 80px;
  }

  .club-initials-avatar {
    width: 80px;
    height: 80px;
    font-size: 1.75rem;
  }
}
</style>
