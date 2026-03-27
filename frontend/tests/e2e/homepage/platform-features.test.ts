import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import PlatformFeatures from '../../../src/components/platform/PlatformFeatures.vue'

describe('PlatformFeatures', () => {
  it('renders all 6 feature card titles', () => {
    const wrapper = mount(PlatformFeatures)
    const expectedTitles = [
      'Multi-Tenant Isolation',
      'Stripe Payments',
      'Member Self-Service',
      'Membership Tiers',
      'Automated Reminders',
      'Admin Dashboard',
    ]
    expectedTitles.forEach((title) => {
      expect(wrapper.text()).toContain(title)
    })
  })

  it('renders all 6 feature card descriptions', () => {
    const wrapper = mount(PlatformFeatures)
    expect(wrapper.text()).toContain('Every club gets its own fully isolated environment.')
    expect(wrapper.text()).toContain("Payments go directly to your club's Stripe account.")
  })

  it('renders 6 feature card elements', () => {
    const wrapper = mount(PlatformFeatures)
    expect(wrapper.findAll('.feature-card').length).toBe(6)
  })

  it('applies AOS slide-up to each card column', () => {
    const wrapper = mount(PlatformFeatures)
    const aosCards = wrapper.findAll('[data-aos="slide-up"]')
    expect(aosCards.length).toBe(6)
  })

  it('has section with id="features"', () => {
    const wrapper = mount(PlatformFeatures)
    expect(wrapper.find('#features').exists()).toBe(true)
  })
})
