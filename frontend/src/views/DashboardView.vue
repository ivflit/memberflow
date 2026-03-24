<template>
  <section class="section">
    <div class="container">
      <h1 class="title">Dashboard</h1>
      <p class="subtitle">Welcome, {{ authStore.user?.first_name }}!</p>
      <button class="button is-light" @click="handleLogout">Sign out</button>
    </div>
  </section>
</template>

<script setup>
import { useAuthStore } from '../stores/auth.js'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

async function handleLogout() {
  await authStore.logout()
  router.push('/login')
}
</script>
