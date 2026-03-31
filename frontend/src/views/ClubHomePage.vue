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
import { ref } from 'vue'
import ClubNavbar from '../components/club/ClubNavbar.vue'
import ClubHero from '../components/club/ClubHero.vue'

const theme = ref(localStorage.getItem('mf-theme') || 'light')

function toggleTheme() {
  theme.value = theme.value === 'dark' ? 'light' : 'dark'
  localStorage.setItem('mf-theme', theme.value)
}
</script>
