/**
 * cashSession store — state machine for daily cash drawer.
 * States: CLOSED → OPEN → PENDING_COUNT → CLOSED (archived)
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { cashApi } from '@/api/cash'
import { useUiStore } from './ui'

export const CASH_SESSION_STATUS = {
    CLOSED: 'closed',
    OPEN: 'open',
    PENDING_COUNT: 'pending_count',
    RECONCILED: 'reconciled',
}

export const useCashSessionStore = defineStore('cashSession', () => {
    const ui = useUiStore()

    const session = ref(null)        // current session object from API
    const entries = ref([])          // inflows + outflows
    const loading = ref(false)
    const countedAmount = ref(null)

    const status = computed(() => session.value?.status || CASH_SESSION_STATUS.CLOSED)
    const isOpen = computed(() => status.value === 'open')

    const sessionInflows = computed(() =>
        (session.value?.entries || entries.value).filter(e => e.type === 'inflow')
    )
    const sessionOutflows = computed(() =>
        (session.value?.entries || entries.value).filter(e => e.type === 'outflow')
    )

    const totalInflows = computed(() =>
        sessionInflows.value.reduce((s, e) => s + Number(e.amount), 0)
    )
    const totalOutflows = computed(() =>
        sessionOutflows.value.reduce((s, e) => s + Number(e.amount), 0)
    )

    const expectedCash = computed(() =>
        Number(session.value?.opening_amount || 0) + totalInflows.value - totalOutflows.value
    )

    const variance = computed(() =>
        countedAmount.value !== null ? countedAmount.value - expectedCash.value : null
    )

    async function fetchCurrent() {
        loading.value = true
        try {
            const { data } = await cashApi.currentSession()
            session.value = data
        } catch (e) {
            if (e.response?.status === 404) {
                session.value = null   // No open session — normal state
            } else {
                throw e
            }
        } finally {
            loading.value = false
        }
    }

    async function openSession(openingAmount) {
        loading.value = true
        try {
            const { data } = await cashApi.openSession({ opening_amount: openingAmount })
            session.value = data
            ui.toastSuccess?.(`Cash session opened with Rs. ${Number(openingAmount).toLocaleString()}`)
        } finally {
            loading.value = false
        }
    }

    async function addInflow(entry) {
        if (!session.value) return
        const { data } = await cashApi.addInflow(session.value.id, entry)
        // Refresh session to get updated totals
        await fetchCurrent()
        return data
    }

    async function addOutflow(entry) {
        if (!session.value) return
        const { data } = await cashApi.addOutflow(session.value.id, entry)
        await fetchCurrent()
        return data
    }

    async function closeSession(counted, notes = '') {
        loading.value = true
        try {
            const { data } = await cashApi.closeSession({
                counted_amount: counted,
                notes,
            })
            session.value = data
            countedAmount.value = counted
            ui.toastSuccess?.('Cash session closed and reconciled')
        } finally {
            loading.value = false
        }
    }

    return {
        session, entries, loading, countedAmount,
        status, isOpen,
        sessionInflows, sessionOutflows,
        totalInflows, totalOutflows,
        expectedCash, variance,
        fetchCurrent, openSession, addInflow, addOutflow, closeSession,
    }
})
