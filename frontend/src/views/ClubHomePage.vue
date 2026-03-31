<template>
  <div
    class="club-page"
    :data-theme="theme"
  >
    <ClubNavbar
      :is-dark="theme === 'dark'"
      @toggle-theme="toggleTheme"
    />
    <main>
      <ClubHero />
    </main>
  </div>
</template>

<script setup>
import ClubNavbar from '../components/club/ClubNavbar.vue'
import ClubHero from '../components/club/ClubHero.vue'
import { useTheme } from '../composables/useTheme.js'

const { theme, toggleTheme } = useTheme()
</script>
