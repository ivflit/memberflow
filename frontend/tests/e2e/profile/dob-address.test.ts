import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import ProfileView from '../../../src/views/ProfileView.vue'
import RegisterView from '../../../src/views/RegisterView.vue'
import SetPasswordView from '../../../src/views/SetPasswordView.vue'

// ── Shared mocks ──────────────────────────────────────────────────────────────

vi.mock('../../../src/stores/tenant.js', () => ({
  useTenantStore: () => ({
    brandName: 'Springfield CC',
    config: { name: 'Springfield CC', branding: { logo_url: null } },
  }),
}))

vi.mock('../../../src/stores/auth.js', () => ({
  useAuthStore: () => ({
    user: { first_name: 'Jane', last_name: 'Doe', email: 'jane@example.com', role: 'member' },
    isAuthenticated: true,
    accessToken: 'fake-token',
    login: vi.fn(),
    logout: vi.fn(),
    register: vi.fn().mockResolvedValue({}),
    setTokens: vi.fn(),
  }),
}))

// Invite mode: token present, mode=invite — DOB/address fields should appear
vi.mock('vue-router', () => ({
  useRouter: () => ({ push: vi.fn() }),
  useRoute: () => ({ query: { token: 'abc123', mode: 'invite' } }),
  RouterLink: { template: '<a><slot /></a>' },
}))

vi.mock('../../../src/composables/useTheme.js', () => ({
  useTheme: () => ({ theme: 'light', toggleTheme: vi.fn() }),
}))

vi.mock('../../../src/api/profile.js', () => ({
  getProfile: vi.fn().mockResolvedValue({
    data: {
      email: 'jane@example.com',
      first_name: 'Jane',
      last_name: 'Doe',
      role: 'member',
      date_of_birth: '1990-06-15',
      address_street: '123 Main St',
      address_city: 'Springfield',
      address_postcode: 'SP1 2AB',
      address_country: 'United Kingdom',
    },
  }),
  updateProfile: vi.fn().mockResolvedValue({
    data: {
      email: 'jane@example.com',
      first_name: 'Jane',
      last_name: 'Doe',
      role: 'member',
      date_of_birth: '1990-06-15',
      address_street: '123 Main St',
      address_city: 'Springfield',
      address_postcode: 'SP1 2AB',
      address_country: 'United Kingdom',
    },
  }),
  changePassword: vi.fn().mockResolvedValue({}),
}))

vi.mock('../../../src/api/client.js', () => ({
  default: {
    post: vi.fn().mockResolvedValue({ data: { access: 'tok', refresh: 'ref', user: {} } }),
  },
}))

// ── Page Object Models ────────────────────────────────────────────────────────

class ProfilePage {
  wrapper: ReturnType<typeof mount>

  constructor(wrapper: ReturnType<typeof mount>) {
    this.wrapper = wrapper
  }

  get dobInput() {
    return this.wrapper.find('input[type="date"]')
  }

  get streetInput() {
    return this.wrapper.find('input[placeholder="123 Main Street"]')
  }

  get cityInput() {
    return this.wrapper.find('input[placeholder="City"]')
  }

  get postcodeInput() {
    return this.wrapper.find('input[placeholder="Postcode"]')
  }

  get countryInput() {
    return this.wrapper.find('input[placeholder="Country"]')
  }

  get addressCard() {
    return this.wrapper.findAll('.profile-card').find(c => c.text().includes('Address'))
  }

  get personalDetailsCard() {
    return this.wrapper.findAll('.profile-card').find(c => c.text().includes('Personal details'))
  }

  get addressSaveButton() {
    return this.addressCard?.find('button[type="submit"]')
  }
}

class RegisterPage {
  wrapper: ReturnType<typeof mount>

  constructor(wrapper: ReturnType<typeof mount>) {
    this.wrapper = wrapper
  }

  get dobInput() {
    return this.wrapper.find('input[type="date"]')
  }

  get streetInput() {
    return this.wrapper.find('input[placeholder="Street address"]')
  }

  get cityInput() {
    return this.wrapper.find('input[placeholder="City"]')
  }

  get postcodeInput() {
    return this.wrapper.find('input[placeholder="Postcode"]')
  }

  get countryInput() {
    return this.wrapper.find('input[placeholder="Country"]')
  }

  get addressSectionLabel() {
    return this.wrapper.find('.auth-section-label')
  }
}

class SetPasswordPage {
  wrapper: ReturnType<typeof mount>

  constructor(wrapper: ReturnType<typeof mount>) {
    this.wrapper = wrapper
  }

  get dobInput() {
    return this.wrapper.find('input[type="date"]')
  }

  get streetInput() {
    return this.wrapper.find('input[placeholder="Street address"]')
  }

  get cityInput() {
    return this.wrapper.find('input[placeholder="City"]')
  }

  get postcodeInput() {
    return this.wrapper.find('input[placeholder="Postcode"]')
  }

  get countryInput() {
    return this.wrapper.find('input[placeholder="Country"]')
  }

  get firstNameInput() {
    return this.wrapper.find('input[placeholder="First name"]')
  }

  get lastNameInput() {
    return this.wrapper.find('input[placeholder="Last name"]')
  }

  get passwordInput() {
    return this.wrapper.find('input[autocomplete="new-password"]')
  }
}

// ── ProfileView tests ─────────────────────────────────────────────────────────

describe('ProfileView — DOB and address fields', () => {
  it('renders a date-of-birth input in Personal details card', () => {
    const wrapper = mount(ProfileView)
    const page = new ProfilePage(wrapper)
    expect(page.dobInput.exists()).toBe(true)
  })

  it('renders a separate Address card', () => {
    const wrapper = mount(ProfileView)
    const page = new ProfilePage(wrapper)
    expect(page.addressCard).toBeDefined()
    expect(page.addressCard?.exists()).toBe(true)
  })

  it('Address card contains all four address inputs', () => {
    const wrapper = mount(ProfileView)
    const page = new ProfilePage(wrapper)
    expect(page.streetInput.exists()).toBe(true)
    expect(page.cityInput.exists()).toBe(true)
    expect(page.postcodeInput.exists()).toBe(true)
    expect(page.countryInput.exists()).toBe(true)
  })

  it('Address card has its own Save address button', () => {
    const wrapper = mount(ProfileView)
    const page = new ProfilePage(wrapper)
    expect(page.addressSaveButton?.exists()).toBe(true)
    expect(page.addressSaveButton?.text()).toContain('Save address')
  })

  it('Personal details card does NOT contain address inputs', () => {
    const wrapper = mount(ProfileView)
    const page = new ProfilePage(wrapper)
    const personalCard = page.personalDetailsCard
    expect(personalCard?.find('input[placeholder="123 Main Street"]').exists()).toBe(false)
  })

  it('DOB input is inside Personal details card, not Address card', () => {
    const wrapper = mount(ProfileView)
    const page = new ProfilePage(wrapper)
    expect(page.personalDetailsCard?.find('input[type="date"]').exists()).toBe(true)
    expect(page.addressCard?.find('input[type="date"]').exists()).toBe(false)
  })
})

// ── RegisterView tests ────────────────────────────────────────────────────────

describe('RegisterView — DOB and address fields', () => {
  it('renders a date-of-birth input', () => {
    const wrapper = mount(RegisterView)
    const page = new RegisterPage(wrapper)
    expect(page.dobInput.exists()).toBe(true)
  })

  it('renders all four address inputs', () => {
    const wrapper = mount(RegisterView)
    const page = new RegisterPage(wrapper)
    expect(page.streetInput.exists()).toBe(true)
    expect(page.cityInput.exists()).toBe(true)
    expect(page.postcodeInput.exists()).toBe(true)
    expect(page.countryInput.exists()).toBe(true)
  })

  it('renders an Address section label', () => {
    const wrapper = mount(RegisterView)
    const page = new RegisterPage(wrapper)
    expect(page.addressSectionLabel.exists()).toBe(true)
    expect(page.addressSectionLabel.text()).toContain('Address')
  })

  it('address inputs are all optional (no required attribute)', () => {
    const wrapper = mount(RegisterView)
    const page = new RegisterPage(wrapper)
    expect(page.streetInput.attributes('required')).toBeUndefined()
    expect(page.cityInput.attributes('required')).toBeUndefined()
    expect(page.postcodeInput.attributes('required')).toBeUndefined()
    expect(page.countryInput.attributes('required')).toBeUndefined()
  })

  it('DOB input is optional (no required attribute)', () => {
    const wrapper = mount(RegisterView)
    const page = new RegisterPage(wrapper)
    expect(page.dobInput.attributes('required')).toBeUndefined()
  })
})

// ── SetPasswordView (invite mode) tests ───────────────────────────────────────
// Route mock above uses mode='invite', so invite-specific fields are rendered.

describe('SetPasswordView — invite mode fields', () => {
  it('renders first name and last name inputs', () => {
    const wrapper = mount(SetPasswordView)
    const page = new SetPasswordPage(wrapper)
    expect(page.firstNameInput.exists()).toBe(true)
    expect(page.lastNameInput.exists()).toBe(true)
  })

  it('renders a date-of-birth input', () => {
    const wrapper = mount(SetPasswordView)
    const page = new SetPasswordPage(wrapper)
    expect(page.dobInput.exists()).toBe(true)
  })

  it('renders all four address inputs', () => {
    const wrapper = mount(SetPasswordView)
    const page = new SetPasswordPage(wrapper)
    expect(page.streetInput.exists()).toBe(true)
    expect(page.cityInput.exists()).toBe(true)
    expect(page.postcodeInput.exists()).toBe(true)
    expect(page.countryInput.exists()).toBe(true)
  })

  it('address and DOB inputs are all optional (no required attribute)', () => {
    const wrapper = mount(SetPasswordView)
    const page = new SetPasswordPage(wrapper)
    expect(page.dobInput.attributes('required')).toBeUndefined()
    expect(page.streetInput.attributes('required')).toBeUndefined()
    expect(page.cityInput.attributes('required')).toBeUndefined()
    expect(page.postcodeInput.attributes('required')).toBeUndefined()
    expect(page.countryInput.attributes('required')).toBeUndefined()
  })

  it('renders the new password input', () => {
    const wrapper = mount(SetPasswordView)
    const page = new SetPasswordPage(wrapper)
    expect(page.passwordInput.exists()).toBe(true)
  })
})
