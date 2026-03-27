import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import ClubHero from '../../../src/components/club/ClubHero.vue'

vi.mock('../../../src/stores/tenant.js', () => ({
  useTenantStore: () => ({
    config: {
      name: 'Springfield CC',
      branding: {},
    },
    brandName: 'Springfield CC',
  }),
}))

describe('ClubHero', () => {
  it('renders club name as H1', () => {
    const wrapper = mount(ClubHero)
    const h1 = wrapper.find('h1')
    expect(h1.exists()).toBe(true)
    expect(h1.text()).toContain('Springfield CC')
  })

  it('renders welcome tagline with club name', () => {
    const wrapper = mount(ClubHero)
    expect(wrapper.text()).toContain('Welcome to Springfield CC')
  })

  it('renders Join Now CTA linking to /register', () => {
    const wrapper = mount(ClubHero)
    const joinBtn = wrapper.find('a[href="/register"]')
    expect(joinBtn.exists()).toBe(true)
    expect(joinBtn.text()).toContain('Join Now')
  })

  it('shows initials avatar when no logo_url configured', () => {
    const wrapper = mount(ClubHero)
    expect(wrapper.find('.club-initials-avatar').exists()).toBe(true)
    expect(wrapper.find('.club-hero-logo').exists()).toBe(false)
  })

  it('renders initials from club name', () => {
    const wrapper = mount(ClubHero)
    // Springfield CC → SC
    expect(wrapper.find('.club-initials-avatar').text()).toContain('SC')
  })

  it('applies data-aos fade-up on content', () => {
    const wrapper = mount(ClubHero)
    expect(wrapper.find('[data-aos="fade-up"]').exists()).toBe(true)
  })
})
