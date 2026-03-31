<template>
  <section
    id="pricing"
    class="section pricing-section"
  >
    <div class="container">
      <div
        class="has-text-centered mb-6"
        data-aos="fade-up"
      >
        <h2 class="title is-2 pricing-heading">
          Simple, transparent pricing
        </h2>
        <p class="subtitle is-5 pricing-subheading">
          No hidden fees. No long-term contracts. Cancel any time.
        </p>
      </div>

      <div class="columns is-centered">
        <div
          v-for="(tier, index) in tiers"
          :key="tier.name"
          class="column is-4-desktop is-10-tablet"
          data-aos="fade-in"
          :data-aos-delay="index * 100"
        >
          <div
            class="pricing-card"
            :class="[{ 'is-featured': tier.featured }, { 'is-hovered': hoveredIndex === index && !tier.featured }]"
            @mouseenter="hoveredIndex = index"
            @mouseleave="hoveredIndex = null"
          >
            <div
              v-if="tier.featured"
              class="featured-badge"
            >
              <span class="tag is-warning has-text-weight-bold">Most Popular</span>
            </div>

            <div class="pricing-header">
              <h3 class="pricing-tier-name">
                {{ tier.name }}
              </h3>
              <div class="pricing-price">
                <span
                  v-if="tier.price"
                  class="price-amount"
                >{{ tier.price }}</span>
                <span
                  v-else
                  class="price-contact"
                >Contact us</span>
                <span
                  v-if="tier.price"
                  class="price-period"
                >/mo</span>
              </div>
              <p class="pricing-tagline">
                {{ tier.tagline }}
              </p>
            </div>

            <ul class="pricing-features">
              <li
                v-for="feature in tier.features"
                :key="feature"
                class="pricing-feature-item"
              >
                <CheckIcon class="check-icon" />
                <span>{{ feature }}</span>
              </li>
            </ul>

            <div class="pricing-cta">
              <a
                class="button is-fullwidth pricing-btn"
                :class="tier.featured ? 'is-featured-btn' : 'is-outline-btn'"
                @click.prevent="scrollToContact"
              >
                {{ tier.cta }}
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import { CheckIcon } from '@heroicons/vue/24/outline'

const hoveredIndex = ref(null)

const tiers = [
  {
    name: 'Starter',
    price: '£XX',
    tagline: 'Perfect for smaller clubs getting started.',
    featured: false,
    cta: 'Get Started',
    features: [
      'Core membership management',
      'Up to 100 members',
      'Stripe payments',
      'Member self-service portal',
      'Email support',
    ],
  },
  {
    name: 'Pro',
    price: '£XX',
    tagline: 'For growing clubs that need more.',
    featured: true,
    cta: 'Get Started',
    features: [
      'Everything in Starter',
      'Unlimited members',
      'Custom branding',
      'Automated email reminders',
      'Priority support',
    ],
  },
  {
    name: 'Enterprise',
    price: null,
    tagline: 'For large organisations with custom needs.',
    featured: false,
    cta: 'Contact Us',
    features: [
      'Everything in Pro',
      'API access',
      'QuickBooks / Sage integration',
      'Dedicated account manager',
      'SLA guarantee',
    ],
  },
]

function scrollToContact() {
  const el = document.querySelector('#contact')
  if (el) el.scrollIntoView({ behavior: 'smooth' })
}
</script>

