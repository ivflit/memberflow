<template>
  <nav
    class="navbar is-fixed-top platform-navbar"
    :class="{ 'is-scrolled': isScrolled }"
    role="navigation"
    aria-label="main navigation"
  >
    <div class="container">
      <div class="navbar-brand">
        <a
          class="navbar-item brand-logo"
          href="/"
        >
          <span class="brand-name">MemberFlow</span>
        </a>

        <a
          role="button"
          class="navbar-burger"
          :class="{ 'is-active': menuOpen }"
          aria-label="menu"
          :aria-expanded="menuOpen"
          @click="menuOpen = !menuOpen"
        >
          <span aria-hidden="true" />
          <span aria-hidden="true" />
          <span aria-hidden="true" />
        </a>
      </div>

      <div
        class="navbar-menu"
        :class="{ 'is-active': menuOpen }"
      >
        <div class="navbar-start mx-auto">
          <a
            class="navbar-item"
            @click.prevent="scrollTo('#features')"
          >Features</a>
          <a
            class="navbar-item"
            @click.prevent="scrollTo('#pricing')"
          >Pricing</a>
          <a
            class="navbar-item"
            @click.prevent="scrollTo('#contact')"
          >Contact</a>
        </div>

        <div class="navbar-end">
          <div class="navbar-item">
            <a
              class="button is-primary get-started-btn"
              @click.prevent="scrollTo('#contact')"
            >
              Get Started
            </a>
          </div>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useScrollPosition } from '../../composables/useScrollPosition.js'

const { scrollY } = useScrollPosition()
const menuOpen = ref(false)

const isScrolled = computed(() => scrollY.value > 50)

function scrollTo(selector) {
  menuOpen.value = false
  const el = document.querySelector(selector)
  if (el) el.scrollIntoView({ behavior: 'smooth' })
}
</script>

<style scoped>
.platform-navbar {
  background: transparent;
  transition: background 0.3s ease, box-shadow 0.3s ease;
  padding: 0.5rem 0;
}

.platform-navbar.is-scrolled {
  background: #ffffff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12);
}

.brand-name {
  font-size: 1.25rem;
  font-weight: 700;
  color: #ffffff;
  letter-spacing: -0.5px;
}

.platform-navbar.is-scrolled .brand-name {
  color: var(--mf-navy);
}

.platform-navbar .navbar-item {
  color: rgba(255, 255, 255, 0.9);
  font-weight: 500;
  cursor: pointer;
}

.platform-navbar.is-scrolled .navbar-item {
  color: var(--mf-text);
}

.platform-navbar .navbar-item:hover {
  color: var(--mf-teal);
  background: transparent;
}

.get-started-btn {
  background: var(--mf-teal);
  border-color: var(--mf-teal);
  color: #ffffff;
  font-weight: 600;
}

.get-started-btn:hover {
  background: #00b396;
  border-color: #00b396;
  color: #ffffff;
}

.navbar-burger span {
  background-color: #ffffff;
}

.platform-navbar.is-scrolled .navbar-burger span {
  background-color: var(--mf-navy);
}
</style>
