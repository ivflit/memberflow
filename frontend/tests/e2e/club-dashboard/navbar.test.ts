import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import DashboardNavbar from '../../../src/components/club/DashboardNavbar.vue'

const mockPush = vi.fn()
const mockLogout = vi.fn()

vi.mock('../../../src/stores/tenant.js', () => ({
  useTenantStore: () => ({
    config: {
      name: 'Springfield CC',
      branding: {},
    },
    brandName: 'Springfield CC',
  }),
}))

vi.mock('../../../src/stores/auth.js', () => ({
  useAuthStore: () => ({
    user: { first_name: 'Jane', last_name: 'Doe', email: 'jane@example.com' },
    logout: mockLogout,
  }),
}))

vi.mock('vue-router', () => ({
  useRouter: () => ({ push: mockPush }),
  useRoute: () => ({ path: '/dashboard' }),
  RouterLink: { template: '<a><slot /></a>' },
}))

// Page Object Model
class DashboardNavbarPage {
  wrapper: ReturnType<typeof mount>

  constructor(wrapper: ReturnType<typeof mount>) {
    this.wrapper = wrapper
  }

  get clubName() {
    return this.wrapper.find('.club-name')
  }

  get avatarBtn() {
    return this.wrapper.find('.avatar-btn')
  }

  get bellBtn() {
    return this.wrapper.find('.bell-btn')
  }

  get avatarDropdown() {
    return this.wrapper.find('.avatar-dropdown')
  }

  get bellDropdown() {
    return this.wrapper.find('.bell-dropdown')
  }

  get hamburger() {
    return this.wrapper.find('.navbar-burger')
  }

  async clickAvatar() {
    await this.avatarBtn.trigger('click')
  }

  async clickBell() {
    await this.bellBtn.trigger('click')
  }
}

describe('DashboardNavbar — E2E smoke', () => {
  let attachedDiv: HTMLDivElement

  beforeEach(() => {
    mockPush.mockReset()
    mockLogout.mockReset()
    attachedDiv = document.createElement('div')
    document.body.appendChild(attachedDiv)
  })

  afterEach(() => {
    document.body.removeChild(attachedDiv)
  })

  function mountNavbar() {
    return mount(DashboardNavbar, { attachTo: attachedDiv })
  }

  it('renders with club name visible', () => {
    const wrapper = mountNavbar()
    const page = new DashboardNavbarPage(wrapper)
    expect(page.clubName.text()).toContain('Springfield CC')
  })

  it('renders user initials from first_name and last_name', () => {
    const wrapper = mountNavbar()
    expect(wrapper.find('.avatar-circle').text()).toBe('JD')
  })

  it('hamburger button is present', () => {
    const wrapper = mountNavbar()
    const page = new DashboardNavbarPage(wrapper)
    expect(page.hamburger.exists()).toBe(true)
  })

  it('clicking avatar opens dropdown with Sign out item', async () => {
    const wrapper = mountNavbar()
    const page = new DashboardNavbarPage(wrapper)

    // Dropdown starts hidden
    expect(page.avatarDropdown.isVisible()).toBe(false)

    await page.clickAvatar()
    expect(page.avatarDropdown.isVisible()).toBe(true)
    expect(page.avatarDropdown.text()).toContain('Sign out')
  })

  it('clicking Sign out calls authStore.logout() and redirects to /login', async () => {
    const wrapper = mountNavbar()
    const page = new DashboardNavbarPage(wrapper)

    await page.clickAvatar()
    const links = page.avatarDropdown.findAll('a')
    const signOutBtn = links.find((l) => l.text().includes('Sign out'))
    expect(signOutBtn).toBeTruthy()

    await signOutBtn!.trigger('click')
    expect(mockLogout).toHaveBeenCalled()
    expect(mockPush).toHaveBeenCalledWith('/login')
  })

  it('clicking bell shows "No notifications yet"', async () => {
    const wrapper = mountNavbar()
    const page = new DashboardNavbarPage(wrapper)

    expect(page.bellDropdown.isVisible()).toBe(false)
    await page.clickBell()
    expect(page.bellDropdown.isVisible()).toBe(true)
    expect(page.bellDropdown.text()).toContain('No notifications yet')
  })

  it('opening bell closes user menu dropdown', async () => {
    const wrapper = mountNavbar()
    const page = new DashboardNavbarPage(wrapper)

    // Open user menu first
    await page.clickAvatar()
    expect(page.avatarDropdown.isVisible()).toBe(true)

    // Now open bell — user menu should close
    await page.clickBell()
    expect(page.bellDropdown.isVisible()).toBe(true)
    expect(page.avatarDropdown.isVisible()).toBe(false)
  })
})
