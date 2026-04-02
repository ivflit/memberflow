<template>
  <div
    class="events-page"
    :data-theme="theme"
  >
    <ClubNavbar
      :is-dark="theme === 'dark'"
      @toggle-theme="toggleTheme"
    />

    <section class="events-content">
      <div class="container">
        <h1 class="events-heading">
          Upcoming Events
        </h1>

        <!-- Filter bar -->
        <div class="events-filter-bar">
          <div class="events-search-wrap">
            <MagnifyingGlassIcon class="events-search-icon" />
            <input
              v-model="searchQuery"
              class="events-input events-search-input"
              type="text"
              placeholder="Search events..."
            >
          </div>

          <div class="events-select-wrap">
            <select
              v-model="selectedCategory"
              class="events-select"
            >
              <option value="">
                All categories
              </option>
              <option
                v-for="cat in categories"
                :key="cat.id"
                :value="cat.id"
              >
                {{ cat.name }}
              </option>
            </select>
            <ChevronDownIcon class="events-select-chevron" />
          </div>

          <div class="events-date-wrap">
            <CalendarIcon class="events-date-icon" />
            <input
              v-model="dateFrom"
              class="events-input events-date-input"
              type="date"
            >
          </div>

          <div class="events-date-wrap">
            <CalendarIcon class="events-date-icon" />
            <input
              v-model="dateTo"
              class="events-input events-date-input"
              type="date"
            >
          </div>

          <a
            v-if="hasActiveFilters"
            class="events-clear-link"
            href="#"
            @click.prevent="clearFilters"
          >Clear filters</a>
        </div>

        <!-- Error state -->
        <div
          v-if="error"
          class="events-error"
        >
          <p>Failed to load events. Please try again.</p>
          <button
            class="button is-primary mt-2"
            @click="fetchEvents"
          >
            Retry
          </button>
        </div>

        <!-- Loading state -->
        <div
          v-else-if="loading"
          class="events-grid"
        >
          <div
            v-for="n in 3"
            :key="n"
            class="event-card-skeleton"
          />
        </div>

        <!-- Empty state: no events at all -->
        <div
          v-else-if="events.length === 0 && !hasActiveFilters"
          class="events-empty"
        >
          <p>No upcoming events</p>
        </div>

        <!-- Empty state: filters active, no results -->
        <div
          v-else-if="events.length === 0 && hasActiveFilters"
          class="events-empty"
        >
          <p>No events match your search</p>
        </div>

        <!-- Event grid -->
        <div
          v-else
          class="events-grid"
        >
          <div
            v-for="event in events"
            :key="event.id"
            class="event-card"
          >
            <!-- Image -->
            <div class="event-card-image">
              <img
                v-if="event.image_url"
                :src="event.image_url"
                :alt="event.title"
                @error="handleImageError($event)"
              >
              <div
                v-else
                class="event-card-image-placeholder"
              />
            </div>

            <!-- Cancelled banner -->
            <div
              v-if="event.status === 'cancelled'"
              class="event-card-cancelled"
            >
              CANCELLED
            </div>

            <div class="event-card-body">
              <!-- Category badge -->
              <span
                v-if="event.category"
                class="event-card-category"
                :style="{ '--category-colour': event.category.colour || 'var(--bulma-primary)' }"
              >
                {{ event.category.name }}
              </span>

              <!-- Members-only lock icon -->
              <span
                v-if="event.is_restricted && !event.is_eligible"
                class="event-card-members-only"
              >
                <LockClosedIcon class="event-lock-icon" />
              </span>

              <h3 class="event-card-title">
                {{ event.title }}
              </h3>

              <div class="event-card-meta">
                <span class="event-card-date">{{ formatDate(event.start_datetime) }}</span>

                <span
                  v-if="event.venue_name"
                  class="event-card-venue"
                >
                  <a
                    v-if="event.venue_postcode"
                    :href="`https://maps.google.com/?q=${encodeURIComponent(event.venue_postcode)}`"
                    target="_blank"
                    rel="noopener noreferrer"
                  >{{ event.venue_name }}</a>
                  <span v-else>{{ event.venue_name }}</span>
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Pagination -->
        <div
          v-if="totalCount > 20"
          class="events-pagination"
        >
          <button
            v-if="prevPage"
            class="button is-light"
            @click="goToPage(currentPage - 1)"
          >
            Previous
          </button>
          <button
            v-if="nextPage"
            class="button is-light"
            @click="goToPage(currentPage + 1)"
          >
            Next
          </button>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { LockClosedIcon, MagnifyingGlassIcon, ChevronDownIcon, CalendarIcon } from '@heroicons/vue/24/outline'
import ClubNavbar from '../components/club/ClubNavbar.vue'
import { getEvents, getCategories } from '../api/events.js'
import { useTheme } from '../composables/useTheme.js'

const { theme, toggleTheme } = useTheme()

const events = ref([])
const categories = ref([])
const loading = ref(true)
const error = ref(false)
const totalCount = ref(0)
const nextPage = ref(null)
const prevPage = ref(null)
const currentPage = ref(1)

const searchQuery = ref('')
const selectedCategory = ref('')
const dateFrom = ref('')
const dateTo = ref('')

let debounceTimer = null

const hasActiveFilters = computed(() =>
  !!searchQuery.value || !!selectedCategory.value || !!dateFrom.value || !!dateTo.value
)

function formatDate(dt) {
  return new Date(dt).toLocaleString('en-GB', {
    weekday: 'short',
    day: 'numeric',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function handleImageError(event) {
  event.target.style.display = 'none'
  const parent = event.target.parentElement
  if (parent) {
    const placeholder = document.createElement('div')
    placeholder.className = 'event-card-image-placeholder'
    parent.appendChild(placeholder)
  }
}

async function fetchEvents() {
  loading.value = true
  error.value = false
  try {
    const params = { page: currentPage.value }
    if (searchQuery.value) params.search = searchQuery.value
    if (selectedCategory.value) params.category = selectedCategory.value
    if (dateFrom.value) params.date_from = dateFrom.value
    if (dateTo.value) params.date_to = dateTo.value

    const { data } = await getEvents(params)
    events.value = data.results
    totalCount.value = data.count
    nextPage.value = data.next
    prevPage.value = data.previous
  } catch {
    error.value = true
  } finally {
    loading.value = false
  }
}

function goToPage(page) {
  currentPage.value = page
  fetchEvents()
}

function clearFilters() {
  searchQuery.value = ''
  selectedCategory.value = ''
  dateFrom.value = ''
  dateTo.value = ''
  currentPage.value = 1
  fetchEvents()
}

// Debounce search input
watch(searchQuery, () => {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    currentPage.value = 1
    fetchEvents()
  }, 300)
})

// Immediate re-fetch on filter changes
watch([selectedCategory, dateFrom, dateTo], () => {
  currentPage.value = 1
  fetchEvents()
})

onMounted(async () => {
  try {
    const { data } = await getCategories()
    categories.value = data
  } catch {
    // categories optional — don't block page
  }
  fetchEvents()
})
</script>
