<template>
  <div class="platform-page">
    <PlatformNavbar />
    <main>
      <PlatformHero />
      <PlatformFeatures />
      <PlatformPricing />
      <PlatformCarousel />
      <PlatformContactForm />
    </main>
    <PlatformFooter />
  </div>
</template>

<script setup>
import PlatformNavbar from '../components/platform/PlatformNavbar.vue'
import PlatformHero from '../components/platform/PlatformHero.vue'
import PlatformFeatures from '../components/platform/PlatformFeatures.vue'
import PlatformPricing from '../components/platform/PlatformPricing.vue'
import PlatformCarousel from '../components/platform/PlatformCarousel.vue'
import PlatformContactForm from '../components/platform/PlatformContactForm.vue'
import PlatformFooter from '../components/platform/PlatformFooter.vue'
</script>

<style scoped>
.platform-page {
  min-height: 100vh;
}
</style>
