import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import ClubNavbar from '../../../src/components/club/ClubNavbar.vue'

vi.mock('../../../src/stores/tenant.js', () => ({
  useTenantStore: () => ({
    config: {
      name: 'Springfield CC',
      branding: {},
    },
    brandName: 'Springfield CC',
  }),
}))

describe('ClubNavbar', () => {
  it('renders the club name', () => {
    const wrapper = mount(ClubNavbar)
    expect(wrapper.text()).toContain('Springfield CC')
  })

  it('renders Log in button linking to /login', () => {
    const wrapper = mount(ClubNavbar)
    const loginBtn = wrapper.find('a[href="/login"]')
    expect(loginBtn.exists()).toBe(true)
    expect(loginBtn.text()).toContain('Log in')
  })

  it('renders Join Now button linking to /register', () => {
    const wrapper = mount(ClubNavbar)
    const joinBtn = wrapper.find('a[href="/register"]')
    expect(joinBtn.exists()).toBe(true)
    expect(joinBtn.text()).toContain('Join Now')
  })

  it('renders hamburger for mobile', () => {
    const wrapper = mount(ClubNavbar)
    expect(wrapper.find('.navbar-burger').exists()).toBe(true)
  })

  it('shows no broken image when logo_url is not configured', () => {
    const wrapper = mount(ClubNavbar)
    // No logo_url in branding — img should not be rendered
    expect(wrapper.find('img').exists()).toBe(false)
  })

  it('toggles menu on hamburger click', async () => {
    const wrapper = mount(ClubNavbar)
    const burger = wrapper.find('.navbar-burger')
    expect(burger.classes()).not.toContain('is-active')
    await burger.trigger('click')
    expect(burger.classes()).toContain('is-active')
  })
})
