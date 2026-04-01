<template>
  <RouterView />
  <DevToggle />
</template>

<script setup>
import { RouterView } from 'vue-router'
import DevToggle from './components/DevToggle.vue'
</script>
