import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router/index.js'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

// Initialise auth from stored token before mounting
import { useAuthStore } from '@/stores/auth'
import { useSyncStore } from '@/stores/sync'

const auth = useAuthStore()
const sync = useSyncStore()

// Wire up network monitor
const cleanupSync = sync.init()

auth.init().finally(() => {
    app.mount('#app')
})
