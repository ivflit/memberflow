import { describe, it, expect, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import ProfileView from '../../../src/views/ProfileView.vue'

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
    logout: vi.fn(),
  }),
}))

vi.mock('vue-router', () => ({
  useRouter: () => ({ push: vi.fn() }),
  useRoute: () => ({ query: {} }),
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
      date_of_birth: null,
      address_street: '',
      address_city: '',
      address_postcode: '',
      address_country: '',
    },
  }),
  updateProfile: vi.fn().mockResolvedValue({ data: {} }),
  changePassword: vi.fn().mockResolvedValue({}),
}))

vi.mock('../../../src/api/events.js', () => ({
  getAgenda: vi.fn().mockResolvedValue({
    data: {
      results: [
        {
          id: 10,
          title: 'Morning Swim',
          start_datetime: '2026-05-12T08:00:00Z',
          venue_name: 'Springfield Pool',
          status: 'published',
        },
        {
          id: 11,
          title: 'Evening Run',
          start_datetime: '2026-05-14T18:00:00Z',
          venue_name: null,
          status: 'published',
        },
      ],
    },
  }),
  getEvents: vi.fn().mockResolvedValue({ data: { count: 0, next: null, previous: null, results: [] } }),
  getCategories: vi.fn().mockResolvedValue({ data: [] }),
  getEvent: vi.fn(),
}))

vi.mock('../../../src/api/client.js', () => ({
  default: { get: vi.fn(), post: vi.fn(), patch: vi.fn() },
}))

// ── Tests ─────────────────────────────────────────────────────────────────────

describe('ProfileView — My Agenda', () => {
  it('renders My Upcoming Events heading', async () => {
    const wrapper = mount(ProfileView)
    await flushPromises()
    expect(wrapper.find('.profile-agenda-title').text()).toBe('My Upcoming Events')
  })

  it('shows loading skeletons before agenda data arrives', () => {
    const wrapper = mount(ProfileView)
    expect(wrapper.findAll('.profile-agenda-skeleton').length).toBe(3)
  })

  it('renders agenda items after data loads', async () => {
    const wrapper = mount(ProfileView)
    await flushPromises()
    const items = wrapper.findAll('.profile-agenda-item')
    expect(items.length).toBe(2)
  })

  it('displays event title in each agenda item', async () => {
    const wrapper = mount(ProfileView)
    await flushPromises()
    const names = wrapper.findAll('.profile-agenda-name')
    expect(names[0].text()).toBe('Morning Swim')
    expect(names[1].text()).toBe('Evening Run')
  })

  it('displays formatted date for each agenda item', async () => {
    const wrapper = mount(ProfileView)
    await flushPromises()
    const dates = wrapper.findAll('.profile-agenda-date')
    expect(dates.length).toBe(2)
    expect(dates[0].text()).toBeTruthy()
  })

  it('displays venue name when present', async () => {
    const wrapper = mount(ProfileView)
    await flushPromises()
    const venues = wrapper.findAll('.profile-agenda-venue')
    expect(venues.some(v => v.text() === 'Springfield Pool')).toBe(true)
  })

  it('does not render venue element when venue_name is null', async () => {
    const wrapper = mount(ProfileView)
    await flushPromises()
    const venues = wrapper.findAll('.profile-agenda-venue')
    // Only 1 venue shown (Morning Swim), not 2
    expect(venues.length).toBe(1)
  })

  it('shows empty state when no agenda events', async () => {
    const { getAgenda } = await import('../../../src/api/events.js')
    vi.mocked(getAgenda).mockResolvedValueOnce({ data: { results: [] } } as any)
    const wrapper = mount(ProfileView)
    await flushPromises()
    expect(wrapper.find('.profile-agenda-empty').exists()).toBe(true)
    expect(wrapper.find('.profile-agenda-empty').text()).toContain('No upcoming events')
  })

  it('silently handles agenda API failure without crashing', async () => {
    const { getAgenda } = await import('../../../src/api/events.js')
    vi.mocked(getAgenda).mockRejectedValueOnce(new Error('Network error'))
    const wrapper = mount(ProfileView)
    await flushPromises()
    // Page should still render — no error thrown
    expect(wrapper.find('.profile-agenda').exists()).toBe(true)
    // Shows empty state since events are empty
    expect(wrapper.find('.profile-agenda-empty').exists()).toBe(true)
  })

  it('agenda section is present alongside profile forms', async () => {
    const wrapper = mount(ProfileView)
    await flushPromises()
    expect(wrapper.find('.profile-agenda').exists()).toBe(true)
    expect(wrapper.find('.profile-forms').exists()).toBe(true)
  })
})
