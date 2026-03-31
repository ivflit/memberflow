<template>
  <section
    id="features"
    class="section features-section"
  >
    <div class="container">
      <div
        class="has-text-centered mb-6"
        data-aos="fade-up"
      >
        <h2 class="title is-2 features-heading">
          Everything your club needs
        </h2>
        <p class="subtitle is-5 features-subheading">
          Built specifically for sports clubs and community organisations.
        </p>
      </div>

      <div class="columns is-multiline">
        <div
          v-for="(feature, index) in features"
          :key="feature.title"
          class="column is-4-desktop is-6-tablet is-12-mobile"
          data-aos="slide-up"
          :data-aos-delay="index * 80"
        >
          <div
            class="feature-card"
            :class="{ 'is-hovered': hoveredIndex === index }"
            @mouseenter="hoveredIndex = index"
            @mouseleave="hoveredIndex = null"
          >
            <div class="feature-icon-wrap">
              <component
                :is="feature.icon"
                class="feature-icon"
              />
            </div>
            <h3 class="feature-title">
              {{ feature.title }}
            </h3>
            <p class="feature-description">
              {{ feature.description }}
            </p>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import {
  ShieldCheckIcon,
  CreditCardIcon,
  UserGroupIcon,
  TagIcon,
  BellAlertIcon,
  ChartBarIcon,
} from '@heroicons/vue/24/outline'

const hoveredIndex = ref(null)

const features = [
  {
    icon: ShieldCheckIcon,
    title: 'Multi-Tenant Isolation',
    description: 'Every club gets its own fully isolated environment.',
  },
  {
    icon: CreditCardIcon,
    title: 'Stripe Payments',
    description: "Payments go directly to your club's Stripe account.",
  },
  {
    icon: UserGroupIcon,
    title: 'Member Self-Service',
    description: 'Members register, pay, and manage their profile themselves.',
  },
  {
    icon: TagIcon,
    title: 'Membership Tiers',
    description: 'Flexible tiers for Full, Junior, Social, or any custom category.',
  },
  {
    icon: BellAlertIcon,
    title: 'Automated Reminders',
    description: 'Expiry and renewal reminders sent automatically.',
  },
  {
    icon: ChartBarIcon,
    title: 'Admin Dashboard',
    description: 'Full visibility of members, payments, and status in one place.',
  },
]
</script>

