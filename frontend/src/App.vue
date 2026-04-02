<template>
  <RouterView />
  <DevToggle />
  <DevLogin />
</template>

<script setup>
import { RouterView } from 'vue-router'
import DevToggle from './components/DevToggle.vue'
import DevLogin from './components/DevLogin.vue'
</script>
