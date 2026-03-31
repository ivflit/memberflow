import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import DashboardView from '../../../src/views/DashboardView.vue'
import DashboardNavbar from '../../../src/components/club/DashboardNavbar.vue'

vi.mock('../../../src/stores/tenant.js', () => ({
  useTenantStore: () => ({
    config: {
      name: 'Springfield CC',
      branding: { logo_url: null },
    },
    brandName: 'Springfield CC',
  }),
}))

vi.mock('../../../src/stores/auth.js', () => ({
  useAuthStore: () => ({
    user: { first_name: 'Jane', last_name: 'Doe', email: 'jane@example.com' },
    logout: vi.fn(),
  }),
}))

vi.mock('vue-router', () => ({
  useRouter: () => ({ push: vi.fn() }),
  useRoute: () => ({ path: '/dashboard' }),
  RouterLink: { template: '<a><slot /></a>' },
}))

// Page Object Model for responsive tests
class ResponsiveDashboardPage {
  wrapper: ReturnType<typeof mount>

  constructor(wrapper: ReturnType<typeof mount>) {
    this.wrapper = wrapper
  }

  get hamburger() {
    return this.wrapper.find('.navbar-burger')
  }

  get cardColumns() {
    return this.wrapper.findAll('.column.is-half-tablet')
  }

  get mobileColumns() {
    return this.wrapper.findAll('.column.is-full-mobile')
  }

  get columnsGrid() {
    return this.wrapper.find('.columns.is-multiline')
  }
}

describe('DashboardView — responsive layout E2E smoke', () => {
  let attachedDiv: HTMLDivElement

  beforeEach(() => {
    attachedDiv = document.createElement('div')
    document.body.appendChild(attachedDiv)
  })

  afterEach(() => {
    document.body.removeChild(attachedDiv)
  })

  it('hamburger burger button is present in the navbar', () => {
    // The hamburger is present regardless of viewport — CSS hides/shows it
    // but the DOM element must exist for mobile layout to work
    const wrapper = mount(DashboardNavbar, { attachTo: attachedDiv })
    const page = new ResponsiveDashboardPage(wrapper)
    expect(page.hamburger.exists()).toBe(true)
    expect(page.hamburger.classes()).toContain('navbar-burger')
  })

  it('cards use is-full-mobile class for single-column stacking on mobile', () => {
    const wrapper = mount(DashboardView, { attachTo: attachedDiv })
    const page = new ResponsiveDashboardPage(wrapper)

    // All four card columns have is-full-mobile for vertical stacking on mobile
    const mobileColumns = page.mobileColumns
    expect(mobileColumns.length).toBe(4)
  })

  it('cards use is-half-tablet class for 2-column layout on tablet and desktop', () => {
    const wrapper = mount(DashboardView, { attachTo: attachedDiv })
    const page = new ResponsiveDashboardPage(wrapper)

    // All four card columns have is-half-tablet for 2-column layout
    const tabletColumns = page.cardColumns
    expect(tabletColumns.length).toBe(4)
  })

  it('card grid uses columns is-multiline for responsive wrapping', () => {
    const wrapper = mount(DashboardView, { attachTo: attachedDiv })
    const page = new ResponsiveDashboardPage(wrapper)
    expect(page.columnsGrid.exists()).toBe(true)
  })

  it('hamburger toggles is-active class on click (mobile menu open)', async () => {
    const wrapper = mount(DashboardNavbar, { attachTo: attachedDiv })
    const page = new ResponsiveDashboardPage(wrapper)

    expect(page.hamburger.classes()).not.toContain('is-active')
    await page.hamburger.trigger('click')
    expect(page.hamburger.classes()).toContain('is-active')
  })
})
