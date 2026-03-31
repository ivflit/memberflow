import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import DashboardView from '../../../src/views/DashboardView.vue'
import MembershipStatusCard from '../../../src/components/club/dashboard/MembershipStatusCard.vue'
import UpcomingEventsCard from '../../../src/components/club/dashboard/UpcomingEventsCard.vue'
import ClubInfoCard from '../../../src/components/club/dashboard/ClubInfoCard.vue'
import QuickActionsCard from '../../../src/components/club/dashboard/QuickActionsCard.vue'

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

// Page Object Model for DashboardView
class DashboardPage {
  wrapper: ReturnType<typeof mount>

  constructor(wrapper: ReturnType<typeof mount>) {
    this.wrapper = wrapper
  }

  get membershipCard() {
    return this.wrapper.findComponent(MembershipStatusCard)
  }

  get eventsCard() {
    return this.wrapper.findComponent(UpcomingEventsCard)
  }

  get clubInfoCard() {
    return this.wrapper.findComponent(ClubInfoCard)
  }

  get quickActionsCard() {
    return this.wrapper.findComponent(QuickActionsCard)
  }
}

describe('DashboardView — card E2E smoke', () => {
  it('all four cards are present in the dashboard DOM', () => {
    const wrapper = mount(DashboardView)
    const page = new DashboardPage(wrapper)

    expect(page.membershipCard.exists()).toBe(true)
    expect(page.eventsCard.exists()).toBe(true)
    expect(page.clubInfoCard.exists()).toBe(true)
    expect(page.quickActionsCard.exists()).toBe(true)
  })

  it('Membership Status card contains placeholder text', () => {
    const wrapper = mount(DashboardView)
    const page = new DashboardPage(wrapper)
    expect(page.membershipCard.text()).toContain('Your membership details will appear here')
  })

  it('Upcoming Events card contains placeholder text', () => {
    const wrapper = mount(DashboardView)
    const page = new DashboardPage(wrapper)
    expect(page.eventsCard.text()).toContain('Events will appear here when available')
  })

  it('Club Info card contains club name from tenant config', () => {
    const wrapper = mount(DashboardView)
    const page = new DashboardPage(wrapper)
    expect(page.clubInfoCard.text()).toContain('Springfield CC')
    expect(page.clubInfoCard.text()).toContain('Welcome to your member portal')
  })

  it('Quick Actions card contains Renew Membership and Update Profile buttons', () => {
    const wrapper = mount(DashboardView)
    const page = new DashboardPage(wrapper)
    expect(page.quickActionsCard.text()).toContain('Renew Membership')
    expect(page.quickActionsCard.text()).toContain('Update Profile')
  })
})

describe('MembershipStatusCard — unit', () => {
  it('renders Membership Status title', () => {
    const wrapper = mount(MembershipStatusCard)
    expect(wrapper.text()).toContain('Membership Status')
  })

  it('renders two skeleton lines', () => {
    const wrapper = mount(MembershipStatusCard)
    const skeletons = wrapper.findAll('.skeleton-line')
    expect(skeletons.length).toBe(2)
  })
})

describe('UpcomingEventsCard — unit', () => {
  it('renders Upcoming Events title', () => {
    const wrapper = mount(UpcomingEventsCard)
    expect(wrapper.text()).toContain('Upcoming Events')
  })

  it('renders three skeleton rows', () => {
    const wrapper = mount(UpcomingEventsCard)
    const skeletons = wrapper.findAll('.skeleton-line')
    expect(skeletons.length).toBe(3)
  })
})

describe('ClubInfoCard — unit', () => {
  it('renders club name', () => {
    const wrapper = mount(ClubInfoCard)
    expect(wrapper.text()).toContain('Springfield CC')
  })

  it('renders welcome text', () => {
    const wrapper = mount(ClubInfoCard)
    expect(wrapper.text()).toContain('Welcome to your member portal')
  })

  it('does not render img when logo_url is null', () => {
    const wrapper = mount(ClubInfoCard)
    expect(wrapper.find('img').exists()).toBe(false)
  })
})

describe('QuickActionsCard — unit', () => {
  it('renders Renew Membership button', () => {
    const wrapper = mount(QuickActionsCard)
    expect(wrapper.text()).toContain('Renew Membership')
  })

  it('renders Update Profile button', () => {
    const wrapper = mount(QuickActionsCard)
    expect(wrapper.text()).toContain('Update Profile')
  })

  it('buttons use is-primary class', () => {
    const wrapper = mount(QuickActionsCard)
    const primaryBtns = wrapper.findAll('.button.is-primary')
    expect(primaryBtns.length).toBeGreaterThanOrEqual(2)
  })
})
