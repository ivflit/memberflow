import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import PlatformContactForm from '../../../src/components/platform/PlatformContactForm.vue'

vi.mock('../../../src/api/contact.js', () => ({
  submitContactForm: vi.fn(),
}))

import { submitContactForm } from '../../../src/api/contact.js'

describe('PlatformContactForm', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders Name, Email, Message fields', () => {
    const wrapper = mount(PlatformContactForm)
    expect(wrapper.find('#contact-name').exists()).toBe(true)
    expect(wrapper.find('#contact-email').exists()).toBe(true)
    expect(wrapper.find('#contact-message').exists()).toBe(true)
  })

  it('has section with id="contact"', () => {
    const wrapper = mount(PlatformContactForm)
    expect(wrapper.find('#contact').exists()).toBe(true)
  })

  it('has a hidden honeypot field', () => {
    const wrapper = mount(PlatformContactForm)
    const honeypot = wrapper.find('.honeypot-field')
    expect(honeypot.exists()).toBe(true)
  })

  it('shows success message after valid submission', async () => {
    ;(submitContactForm as ReturnType<typeof vi.fn>).mockResolvedValue({ data: { detail: "Thanks! We'll be in touch soon." } })

    const wrapper = mount(PlatformContactForm)
    await wrapper.find('#contact-name').setValue('Jane Smith')
    await wrapper.find('#contact-email').setValue('jane@example.com')
    await wrapper.find('#contact-message').setValue('I am interested in MemberFlow for our club membership management.')

    await wrapper.find('form').trigger('submit')
    await flushPromises()

    expect(wrapper.find('.success-message').exists()).toBe(true)
    expect(wrapper.text()).toContain("Thanks! We'll be in touch soon.")
    expect(wrapper.find('form').exists()).toBe(false)
  })

  it('shows inline error on 400 response with email error', async () => {
    const error = {
      response: {
        status: 400,
        data: { email: ["That email domain doesn't appear to exist. Please check and try again."] },
      },
    }
    ;(submitContactForm as ReturnType<typeof vi.fn>).mockRejectedValue(error)

    const wrapper = mount(PlatformContactForm)
    await wrapper.find('#contact-name').setValue('Jane Smith')
    await wrapper.find('#contact-email').setValue('jane@fakedomain123.xyz')
    await wrapper.find('#contact-message').setValue('I am interested in MemberFlow for our club.')

    await wrapper.find('form').trigger('submit')
    await flushPromises()

    expect(wrapper.find('.help.is-danger').exists()).toBe(true)
    expect(wrapper.text()).toContain("That email domain doesn't appear to exist")
  })

  it('shows rate limit banner on 429 response', async () => {
    const error = { response: { status: 429, data: {} } }
    ;(submitContactForm as ReturnType<typeof vi.fn>).mockRejectedValue(error)

    const wrapper = mount(PlatformContactForm)
    await wrapper.find('#contact-name').setValue('Jane Smith')
    await wrapper.find('#contact-email').setValue('jane@example.com')
    await wrapper.find('#contact-message').setValue('I am interested in MemberFlow for our club.')

    await wrapper.find('form').trigger('submit')
    await flushPromises()

    expect(wrapper.find('.rate-limit-banner').exists()).toBe(true)
    expect(wrapper.text()).toContain('Too many requests')
  })
})
