<template>
  <RouterView v-slot="{ Component }">
    <Transition
      name="page-fade"
      mode="out-in"
    >
      <component :is="Component" />
    </Transition>
  </RouterView>
  <DevToggle />
</template>

<script setup>
import { RouterView } from 'vue-router'
import DevToggle from './components/DevToggle.vue'
</script>
