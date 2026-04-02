import { describe, it, expect, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import EventsView from '../../../src/views/EventsView.vue'

// ── Shared mocks ──────────────────────────────────────────────────────────────

vi.mock('../../../src/stores/tenant.js', () => ({
  useTenantStore: () => ({
    brandName: 'Springfield CC',
    config: { name: 'Springfield CC', branding: { logo_url: null } },
  }),
}))

vi.mock('../../../src/stores/auth.js', () => ({
  useAuthStore: () => ({
    user: null,
    isAuthenticated: false,
    accessToken: null,
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

vi.mock('../../../src/api/events.js', () => ({
  getEvents: vi.fn().mockResolvedValue({
    data: {
      count: 3,
      next: null,
      previous: null,
      results: [
        {
          id: 1,
          title: 'Club Training',
          start_datetime: '2026-05-10T10:00:00Z',
          end_datetime: '2026-05-10T12:00:00Z',
          venue_name: 'Springfield Gym',
          venue_postcode: 'SP1 2AB',
          image_url: null,
          status: 'published',
          category: { id: 1, name: 'Training', colour: '#3273dc' },
          is_restricted: false,
          is_eligible: true,
        },
        {
          id: 2,
          title: 'Members Only Gala',
          start_datetime: '2026-05-15T18:00:00Z',
          end_datetime: '2026-05-15T21:00:00Z',
          venue_name: null,
          venue_postcode: null,
          image_url: 'https://example.com/gala.jpg',
          status: 'published',
          category: null,
          is_restricted: true,
          is_eligible: false,
        },
        {
          id: 3,
          title: 'Annual Dinner',
          start_datetime: '2026-06-01T19:00:00Z',
          end_datetime: '2026-06-01T22:00:00Z',
          venue_name: 'Town Hall',
          venue_postcode: null,
          image_url: null,
          status: 'cancelled',
          category: null,
          is_restricted: false,
          is_eligible: true,
        },
      ],
    },
  }),
  getCategories: vi.fn().mockResolvedValue({
    data: [{ id: 1, name: 'Training', colour: '#3273dc' }],
  }),
  getEvent: vi.fn(),
  getAgenda: vi.fn().mockResolvedValue({ data: { results: [] } }),
}))

vi.mock('../../../src/api/client.js', () => ({
  default: { get: vi.fn(), post: vi.fn(), patch: vi.fn() },
}))

// ── Page Object Model ─────────────────────────────────────────────────────────

class EventsPage {
  wrapper: ReturnType<typeof mount>

  constructor(wrapper: ReturnType<typeof mount>) {
    this.wrapper = wrapper
  }

  get heading() { return this.wrapper.find('.events-heading') }
  get filterBar() { return this.wrapper.find('.events-filter-bar') }
  get searchInput() { return this.wrapper.find('input[type="text"]') }
  get categorySelect() { return this.wrapper.find('select') }
  get dateFromInput() { return this.wrapper.find('input[type="date"]') }
  get eventCards() { return this.wrapper.findAll('.event-card') }
  get emptyState() { return this.wrapper.find('.events-empty') }
  get errorState() { return this.wrapper.find('.events-error') }
  get loadingSkeletons() { return this.wrapper.findAll('.event-card-skeleton') }
  get cancelledBanners() { return this.wrapper.findAll('.event-card-cancelled') }
  get lockBadges() { return this.wrapper.findAll('.event-card-members-only') }
  get categoryBadges() { return this.wrapper.findAll('.event-card-category') }
  get pagination() { return this.wrapper.find('.events-pagination') }
}

// ── Tests ─────────────────────────────────────────────────────────────────────

describe('EventsView — E2E smoke', () => {
  it('renders the page heading', async () => {
    const wrapper = mount(EventsView)
    expect(wrapper.find('.events-heading').text()).toBe('Upcoming Events')
  })

  it('renders search input and filter bar', async () => {
    const wrapper = mount(EventsView)
    const page = new EventsPage(wrapper)
    expect(page.filterBar.exists()).toBe(true)
    expect(page.searchInput.exists()).toBe(true)
    expect(page.categorySelect.exists()).toBe(true)
  })

  it('shows loading skeletons before data arrives', () => {
    const wrapper = mount(EventsView)
    const page = new EventsPage(wrapper)
    expect(page.loadingSkeletons.length).toBe(3)
  })

  it('renders event cards after data loads', async () => {
    const wrapper = mount(EventsView)
    await flushPromises()
    const page = new EventsPage(wrapper)
    expect(page.eventCards.length).toBe(3)
  })

  it('renders category badge on event with category', async () => {
    const wrapper = mount(EventsView)
    await flushPromises()
    const page = new EventsPage(wrapper)
    expect(page.categoryBadges.length).toBeGreaterThanOrEqual(1)
    expect(page.categoryBadges[0].text()).toBe('Training')
  })

  it('renders cancelled banner on cancelled event', async () => {
    const wrapper = mount(EventsView)
    await flushPromises()
    const page = new EventsPage(wrapper)
    expect(page.cancelledBanners.length).toBe(1)
    expect(page.cancelledBanners[0].text()).toBe('CANCELLED')
  })

  it('renders members-only lock badge on restricted ineligible event', async () => {
    const wrapper = mount(EventsView)
    await flushPromises()
    const page = new EventsPage(wrapper)
    expect(page.lockBadges.length).toBe(1)
  })

  it('renders venue as Google Maps link when postcode present', async () => {
    const wrapper = mount(EventsView)
    await flushPromises()
    const venueLink = wrapper.find('.event-card-venue a')
    expect(venueLink.exists()).toBe(true)
    expect(venueLink.text()).toBe('Springfield Gym')
    expect(venueLink.attributes('href')).toContain('maps.google.com')
  })

  it('renders venue as plain text when no postcode', async () => {
    const wrapper = mount(EventsView)
    await flushPromises()
    const venuePlain = wrapper.findAll('.event-card-venue span')
    expect(venuePlain.some(el => el.text() === 'Town Hall')).toBe(true)
  })

  it('does not show pagination when count <= 20', async () => {
    const wrapper = mount(EventsView)
    await flushPromises()
    const page = new EventsPage(wrapper)
    expect(page.pagination.exists()).toBe(false)
  })

  it('shows empty state when no events and no active filters', async () => {
    const { getEvents } = await import('../../../src/api/events.js')
    vi.mocked(getEvents).mockResolvedValueOnce({
      data: { count: 0, next: null, previous: null, results: [] },
    } as any)
    const wrapper = mount(EventsView)
    await flushPromises()
    expect(wrapper.find('.events-empty').text()).toContain('No upcoming events')
  })

  it('shows no-results message when filters active with empty results', async () => {
    const { getEvents } = await import('../../../src/api/events.js')
    vi.mocked(getEvents).mockResolvedValueOnce({
      data: { count: 0, next: null, previous: null, results: [] },
    } as any)
    const wrapper = mount(EventsView)
    await flushPromises()
    // Set a filter so hasActiveFilters is true
    await wrapper.find('input[type="text"]').setValue('xyz')
    await flushPromises()
    expect(wrapper.find('.events-empty').text()).toContain('No events match your search')
  })

  it('shows error state when API call fails', async () => {
    const { getEvents } = await import('../../../src/api/events.js')
    vi.mocked(getEvents).mockRejectedValueOnce(new Error('Network error'))
    const wrapper = mount(EventsView)
    await flushPromises()
    expect(wrapper.find('.events-error').exists()).toBe(true)
    expect(wrapper.find('.events-error').text()).toContain('Failed to load events')
  })

  it('shows retry button in error state', async () => {
    const { getEvents } = await import('../../../src/api/events.js')
    vi.mocked(getEvents).mockRejectedValueOnce(new Error('Network error'))
    const wrapper = mount(EventsView)
    await flushPromises()
    expect(wrapper.find('.events-error .button').exists()).toBe(true)
  })

  it('populates category dropdown with fetched categories', async () => {
    const wrapper = mount(EventsView)
    await flushPromises()
    const options = wrapper.findAll('select option')
    expect(options.some(o => o.text() === 'Training')).toBe(true)
  })

  it('shows clear filters link when search is active', async () => {
    const wrapper = mount(EventsView)
    await flushPromises()
    await wrapper.find('input[type="text"]').setValue('test')
    expect(wrapper.find('.events-clear-link').exists()).toBe(true)
  })
})
