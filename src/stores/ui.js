/**
 * Global UI state: sidebar collapse, toast notifications, modal confirm dialog,
 * step-up auth dialog.
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUiStore = defineStore('ui', () => {
    // ── Sidebar ────────────────────────────────────────────────────────────────
    const sidebarOpen = ref(true)
    function toggleSidebar() { sidebarOpen.value = !sidebarOpen.value }

    // ── Toast Notifications ────────────────────────────────────────────────────
    const toasts = ref([])
    let toastSeq = 0

    function toast({ message, type = 'info', duration = 4000 }) {
        const id = ++toastSeq
        toasts.value.push({ id, message, type })
        setTimeout(() => dismissToast(id), duration)
    }
    function dismissToast(id) {
        toasts.value = toasts.value.filter(t => t.id !== id)
    }

    const toastSuccess = (message) => toast({ message, type: 'success' })
    const toastError = (message) => toast({ message, type: 'error', duration: 7000 })
    const toastWarn = (message) => toast({ message, type: 'warning', duration: 5000 })
    const toastInfo = (message) => toast({ message, type: 'info' })

    // ── Confirm Dialog ─────────────────────────────────────────────────────────
    const confirmDialog = ref({
        open: false, title: '', message: '', effect: null,
        confirmLabel: 'Confirm', confirmClass: 'btn-danger', resolve: null,
    })

    function confirm({ title, message, effect = null, confirmLabel = 'Confirm', confirmClass = 'btn-danger' }) {
        return new Promise((resolve) => {
            confirmDialog.value = { open: true, title, message, effect, confirmLabel, confirmClass, resolve }
        })
    }

    function resolveConfirm(value) {
        confirmDialog.value.resolve?.(value)
        confirmDialog.value = { ...confirmDialog.value, open: false, resolve: null }
    }

    // ── Step-Up Auth Dialog ────────────────────────────────────────────────────
    /**
     * stepUpAuthDialog state:
     * { open, action, resolve }
     * action: string describing what requires elevated auth
     * resolve: Function<boolean>
     */
    const stepUpAuthDialog = ref({
        open: false,
        action: '',
        resolve: null,
    })

    function requireStepUp(action) {
        return new Promise((resolve) => {
            stepUpAuthDialog.value = { open: true, action, resolve }
        })
    }

    function resolveStepUp(value) {
        stepUpAuthDialog.value.resolve?.(value)
        stepUpAuthDialog.value = { open: false, action: '', resolve: null }
    }

    // ── Loading overlay ────────────────────────────────────────────────────────
    const globalLoading = ref(false)

    return {
        sidebarOpen, toggleSidebar,
        toasts, toast, dismissToast, toastSuccess, toastError, toastWarn, toastInfo,
        confirmDialog, confirm, resolveConfirm,
        stepUpAuthDialog, requireStepUp, resolveStepUp,
        globalLoading,
    }
})
