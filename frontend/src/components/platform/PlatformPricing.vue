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

<style scoped>
.pricing-section {
  background: #ffffff;
  padding: 5rem 1.5rem;
}

.pricing-heading {
  color: var(--mf-navy);
  font-weight: 800;
}

.pricing-subheading {
  color: var(--mf-text);
  max-width: 480px;
  margin-left: auto;
  margin-right: auto;
}

.pricing-card {
  background: #ffffff;
  border: 2px solid #e8edf2;
  border-radius: 16px;
  padding: 2.5rem 2rem;
  height: 100%;
  display: flex;
  flex-direction: column;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  position: relative;
}

.pricing-card.is-featured {
  border-color: var(--mf-teal);
  box-shadow: 0 8px 32px rgba(0, 201, 167, 0.18);
}

.pricing-card.is-hovered {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.1);
}

.featured-badge {
  position: absolute;
  top: -14px;
  left: 50%;
  transform: translateX(-50%);
}

.pricing-header {
  margin-bottom: 1.75rem;
  text-align: center;
}

.pricing-tier-name {
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--mf-navy);
  margin-bottom: 0.75rem;
}

.pricing-price {
  display: flex;
  align-items: baseline;
  justify-content: center;
  gap: 0.25rem;
  margin-bottom: 0.5rem;
}

.price-amount {
  font-size: 2.5rem;
  font-weight: 800;
  color: var(--mf-navy);
  line-height: 1;
}

.price-contact {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--mf-navy);
}

.price-period {
  font-size: 1rem;
  color: var(--mf-text);
  font-weight: 500;
}

.pricing-tagline {
  font-size: 0.9rem;
  color: var(--mf-text);
  margin-top: 0.5rem;
}

.pricing-features {
  list-style: none;
  padding: 0;
  margin: 0 0 2rem;
  flex: 1;
}

.pricing-feature-item {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.45rem 0;
  font-size: 0.92rem;
  color: var(--mf-text);
  border-bottom: 1px solid #f0f4f8;
}

.pricing-feature-item:last-child {
  border-bottom: none;
}

.check-icon {
  width: 1.1rem;
  height: 1.1rem;
  color: var(--mf-teal);
  flex-shrink: 0;
  stroke-width: 2.5;
}

.pricing-btn {
  border-radius: 8px;
  font-weight: 600;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.pricing-btn.is-featured-btn {
  background: var(--mf-teal);
  border-color: var(--mf-teal);
  color: #ffffff;
}

.pricing-btn.is-featured-btn:hover {
  background: #00b396;
  border-color: #00b396;
  color: #ffffff;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 201, 167, 0.3);
}

.pricing-btn.is-outline-btn {
  background: transparent;
  border-color: var(--mf-navy);
  color: var(--mf-navy);
}

.pricing-btn.is-outline-btn:hover {
  background: var(--mf-navy);
  color: #ffffff;
}
</style>
