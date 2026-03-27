import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import PlatformCarousel from '../../../src/components/platform/PlatformCarousel.vue'

describe('PlatformCarousel', () => {
  it('renders the section heading', () => {
    const wrapper = mount(PlatformCarousel)
    expect(wrapper.text()).toContain('Trusted by clubs & organisations')
  })

  it('renders the logo track', () => {
    const wrapper = mount(PlatformCarousel)
    expect(wrapper.find('.logo-track').exists()).toBe(true)
  })

  it('renders 8 unique logos (duplicated for loop = 16 items)', () => {
    const wrapper = mount(PlatformCarousel)
    expect(wrapper.findAll('.logo-item').length).toBe(16)
  })

  it('marquee-wrapper has aria-hidden for decorative content', () => {
    const wrapper = mount(PlatformCarousel)
    const marquee = wrapper.find('.marquee-wrapper')
    expect(marquee.attributes('aria-hidden')).toBe('true')
  })
})
