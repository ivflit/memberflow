import { createApp } from 'vue'
import { createPinia } from 'pinia'
import AOS from 'aos'
import 'aos/dist/aos.css'
import App from './App.vue'
import router from './router/index.js'
import './styles/main.scss'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

// Bootstrap tenant config before mounting — must complete before any component renders
const { useTenantStore } = await import('./stores/tenant.js')
const tenantStore = useTenantStore()
await tenantStore.bootstrap()

// Initialise AOS after tenant bootstrap
AOS.init({ duration: 800, once: true })

app.mount('#app')
