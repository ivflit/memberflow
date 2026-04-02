<template>
  <ClubNavbar
    :is-dark="isDark"
    @toggle-theme="$emit('toggle-theme')"
  />
</template>

<script setup>
import ClubNavbar from './ClubNavbar.vue'
defineProps({ isDark: { type: Boolean, default: false } })
defineEmits(['toggle-theme'])
</script>
