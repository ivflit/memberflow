<template>
  <div class="club-page">
    <ClubNavbar />
    <main>
      <ClubHero />
    </main>
  </div>
</template>

<script setup>
import ClubNavbar from '../components/club/ClubNavbar.vue'
import ClubHero from '../components/club/ClubHero.vue'
</script>

<style scoped>
.club-page {
  min-height: 100vh;
}
</style>
