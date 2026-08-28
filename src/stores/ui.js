/**
 * Global UI state: sidebar collapse, toast notifications, modal confirm dialog.
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

    // Shortcuts
    const toastSuccess = (message) => toast({ message, type: 'success' })
    const toastError = (message) => toast({ message, type: 'error', duration: 7000 })
    const toastWarn = (message) => toast({ message, type: 'warning', duration: 5000 })
    const toastInfo = (message) => toast({ message, type: 'info' })

    // ── Confirm Dialog ─────────────────────────────────────────────────────────
    /**
     * confirmDialog state shape:
     * {
     *   open: bool,
     *   title: string,
     *   message: string,        // plain description
     *   effect: string|null,    // financial/inventory effect text (required for destructive actions)
     *   confirmLabel: string,
     *   confirmClass: string,   // btn-danger | btn-primary
     *   resolve: Function,
     * }
     */
    const confirmDialog = ref({
        open: false, title: '', message: '', effect: null,
        confirmLabel: 'Confirm', confirmClass: 'btn-danger', resolve: null,
    })

    /**
     * Show a confirmation dialog. Returns a Promise<boolean>.
     * For destructive actions, pass `effect` to show financial/inventory impact.
     */
    function confirm({ title, message, effect = null, confirmLabel = 'Confirm', confirmClass = 'btn-danger' }) {
        return new Promise((resolve) => {
            confirmDialog.value = { open: true, title, message, effect, confirmLabel, confirmClass, resolve }
        })
    }

    function resolveConfirm(value) {
        confirmDialog.value.resolve?.(value)
        confirmDialog.value = { ...confirmDialog.value, open: false, resolve: null }
    }

    // ── Loading overlay ────────────────────────────────────────────────────────
    const globalLoading = ref(false)

    return {
        sidebarOpen, toggleSidebar,
        toasts, toast, dismissToast, toastSuccess, toastError, toastWarn, toastInfo,
        confirmDialog, confirm, resolveConfirm,
        globalLoading,
    }
})
