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
