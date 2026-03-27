import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import PlatformPricing from '../../../src/components/platform/PlatformPricing.vue'

describe('PlatformPricing', () => {
  it('renders all 3 pricing tier names', () => {
    const wrapper = mount(PlatformPricing)
    expect(wrapper.text()).toContain('Starter')
    expect(wrapper.text()).toContain('Pro')
    expect(wrapper.text()).toContain('Enterprise')
  })

  it('renders 3 pricing card elements', () => {
    const wrapper = mount(PlatformPricing)
    expect(wrapper.findAll('.pricing-card').length).toBe(3)
  })

  it('Pro card has "Most Popular" badge', () => {
    const wrapper = mount(PlatformPricing)
    expect(wrapper.text()).toContain('Most Popular')
    expect(wrapper.find('.featured-badge').exists()).toBe(true)
  })

  it('Pro card has is-featured class', () => {
    const wrapper = mount(PlatformPricing)
    const featuredCard = wrapper.find('.pricing-card.is-featured')
    expect(featuredCard.exists()).toBe(true)
  })

  it('renders CTA buttons for each tier', () => {
    const wrapper = mount(PlatformPricing)
    const ctaButtons = wrapper.findAll('.pricing-btn')
    expect(ctaButtons.length).toBe(3)
  })

  it('has section with id="pricing"', () => {
    const wrapper = mount(PlatformPricing)
    expect(wrapper.find('#pricing').exists()).toBe(true)
  })
})
