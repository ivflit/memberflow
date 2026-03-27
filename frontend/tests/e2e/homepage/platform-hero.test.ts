import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import PlatformHero from '../../../src/components/platform/PlatformHero.vue'

describe('PlatformHero', () => {
  it('renders the headline', () => {
    const wrapper = mount(PlatformHero)
    expect(wrapper.text()).toContain('Membership management, built for clubs.')
  })

  it('renders the sub-headline mentioning spreadsheets', () => {
    const wrapper = mount(PlatformHero)
    expect(wrapper.text()).toContain('Stop chasing spreadsheets')
  })

  it('renders Get Started CTA button', () => {
    const wrapper = mount(PlatformHero)
    expect(wrapper.text()).toContain('Get Started')
  })

  it('applies data-aos fade-up to content container', () => {
    const wrapper = mount(PlatformHero)
    const aosEl = wrapper.find('[data-aos="fade-up"]')
    expect(aosEl.exists()).toBe(true)
  })

  it('Get Started button triggers smooth scroll to #contact', async () => {
    const mockScrollIntoView = vi.fn()
    const mockQuerySelector = vi.spyOn(document, 'querySelector').mockReturnValue({
      scrollIntoView: mockScrollIntoView,
    } as unknown as Element)

    const wrapper = mount(PlatformHero)
    await wrapper.find('.hero-cta').trigger('click')

    expect(mockQuerySelector).toHaveBeenCalledWith('#contact')
    expect(mockScrollIntoView).toHaveBeenCalledWith({ behavior: 'smooth' })

    mockQuerySelector.mockRestore()
  })
})
