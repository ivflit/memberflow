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

