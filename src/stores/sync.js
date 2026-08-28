/**
 * Sync / connectivity status store.
 * Combines browser online/offline events with active request tracking
 * to show a persistent, always-visible status: Online | Offline | Syncing | Pending | Error
 */
import { defineStore } from 'pinia'
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { onPendingChange } from '@/api/client'
import { SYNC_STATE } from '@/utils/constants'

export const useSyncStore = defineStore('sync', () => {
    const networkOnline = ref(navigator.onLine)
    const pendingRequests = ref(0)
    const hasError = ref(false)
    const errorMessage = ref('')

    const status = computed(() => {
        if (!networkOnline.value) return SYNC_STATE.OFFLINE
        if (hasError.value) return SYNC_STATE.ERROR
        if (pendingRequests.value > 0) return SYNC_STATE.SYNCING
        return SYNC_STATE.ONLINE
    })

    function setError(msg = '') {
        hasError.value = true
        errorMessage.value = msg
        setTimeout(() => { hasError.value = false; errorMessage.value = '' }, 8000)
    }

    function clearError() {
        hasError.value = false
        errorMessage.value = ''
    }

    function init() {
        const handleOnline = () => { networkOnline.value = true }
        const handleOffline = () => { networkOnline.value = false }
        window.addEventListener('online', handleOnline)
        window.addEventListener('offline', handleOffline)

        const unsub = onPendingChange((count) => { pendingRequests.value = count })

        return () => {
            window.removeEventListener('online', handleOnline)
            window.removeEventListener('offline', handleOffline)
            unsub()
        }
    }

    return { networkOnline, pendingRequests, hasError, errorMessage, status, setError, clearError, init }
})
