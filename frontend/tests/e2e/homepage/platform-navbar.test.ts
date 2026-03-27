import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import PlatformNavbar from '../../../src/components/platform/PlatformNavbar.vue'

vi.mock('../../../src/composables/useScrollPosition.js', () => ({
  useScrollPosition: () => ({ scrollY: { value: 0 } }),
}))

describe('PlatformNavbar', () => {
  it('renders MemberFlow brand logo', () => {
    const wrapper = mount(PlatformNavbar)
    expect(wrapper.text()).toContain('MemberFlow')
  })

  it('renders Features, Pricing, Contact nav links', () => {
    const wrapper = mount(PlatformNavbar)
    expect(wrapper.text()).toContain('Features')
    expect(wrapper.text()).toContain('Pricing')
    expect(wrapper.text()).toContain('Contact')
  })

  it('renders Get Started CTA button', () => {
    const wrapper = mount(PlatformNavbar)
    expect(wrapper.text()).toContain('Get Started')
  })

  it('has a navbar-burger element for mobile', () => {
    const wrapper = mount(PlatformNavbar)
    expect(wrapper.find('.navbar-burger').exists()).toBe(true)
  })

  it('toggles mobile menu when burger is clicked', async () => {
    const wrapper = mount(PlatformNavbar)
    const burger = wrapper.find('.navbar-burger')
    expect(burger.classes()).not.toContain('is-active')
    await burger.trigger('click')
    expect(burger.classes()).toContain('is-active')
    expect(wrapper.find('.navbar-menu').classes()).toContain('is-active')
  })
})
