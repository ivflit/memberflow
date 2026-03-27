import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import PlatformFooter from '../../../src/components/platform/PlatformFooter.vue'

describe('PlatformFooter', () => {
  it('renders MemberFlow brand name', () => {
    const wrapper = mount(PlatformFooter)
    expect(wrapper.text()).toContain('MemberFlow')
  })

  it('renders copyright line', () => {
    const wrapper = mount(PlatformFooter)
    expect(wrapper.text()).toContain('2026 MemberFlow')
  })

  it('renders tagline', () => {
    const wrapper = mount(PlatformFooter)
    expect(wrapper.text()).toContain('Membership management, built for clubs.')
  })

  it('renders Product column links', () => {
    const wrapper = mount(PlatformFooter)
    expect(wrapper.text()).toContain('Product')
    expect(wrapper.text()).toContain('Features')
    expect(wrapper.text()).toContain('Pricing')
  })

  it('renders Company column links', () => {
    const wrapper = mount(PlatformFooter)
    expect(wrapper.text()).toContain('Company')
    expect(wrapper.text()).toContain('About')
  })

  it('renders social links section', () => {
    const wrapper = mount(PlatformFooter)
    expect(wrapper.findAll('.social-link').length).toBe(3)
  })

  it('renders footer element with correct class', () => {
    const wrapper = mount(PlatformFooter)
    expect(wrapper.find('footer.platform-footer').exists()).toBe(true)
  })
})
