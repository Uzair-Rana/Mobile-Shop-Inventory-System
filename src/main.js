import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router/index.js'
import { useAuthStore } from '@/stores/auth'
import { useSyncStore } from '@/stores/sync'

async function startMSW() {
    try {
        const { worker } = await import('./api/mock/browser.js')
        await worker.start({
            onUnhandledRequest: 'bypass',
            serviceWorker: { url: '/mockServiceWorker.js' },
        })
        console.info('[MSW] Mock API active — VITE_USE_MOCK=true')
    } catch (e) {
        console.warn('[MSW] Failed to start mock worker, continuing without it:', e)
    }
}

async function bootstrap() {
    // Only start mock API when explicitly enabled
    if (import.meta.env.VITE_USE_MOCK === 'true') {
        await startMSW()
    }

    const app = createApp(App)
    const pinia = createPinia()

    app.use(pinia)
    app.use(router)

    const auth = useAuthStore()
    const sync = useSyncStore()

    sync.init()

    try {
        await auth.init()
    } catch (e) {
        console.warn('[Auth] init failed, mounting anyway:', e)
    }

    app.mount('#app')
}

bootstrap().catch(err => {
    console.error('[Bootstrap] Fatal error, mounting bare app:', err)
    const app = createApp(App)
    app.use(createPinia())
    app.use(router)
    app.mount('#app')
})
