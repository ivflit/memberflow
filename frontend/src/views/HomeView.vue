<template>
  <div style="font-family: monospace; padding: 2rem;">
    <p>{{ message }}</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import client from '../api/client.js'

const message = ref('Connecting...')

onMounted(async () => {
  try {
    const { data } = await client.get('/api/v1/health/')
    message.value = `Connected to tenant: ${data.tenant}`
  } catch {
    message.value = 'API unreachable'
  }
})
</script>
