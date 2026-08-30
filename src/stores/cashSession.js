/**
 * cashSession store — state machine for daily cash drawer.
 * States: CLOSED → OPEN → PENDING_COUNT → RECONCILED
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useMockDataStore } from './mockData'
import { useUiStore } from './ui'

export const CASH_SESSION_STATUS = {
    CLOSED: 'closed',
    OPEN: 'open',
    PENDING_COUNT: 'pending_count',
    RECONCILED: 'reconciled',
}

export const useCashSessionStore = defineStore('cashSession', () => {
    const mock = useMockDataStore()
    const ui = useUiStore()

    // Load from mock data
    const activeSession = ref(
        mock.cashSessions.find(s => s.status === 'open') || null
    )
    const status = ref(activeSession.value ? CASH_SESSION_STATUS.OPEN : CASH_SESSION_STATUS.CLOSED)
    const inflows = ref([...mock.cashInflows])
    const outflows = ref([...mock.cashOutflows])
    const countedAmount = ref(null)
    const openingAmount = ref(0)

    const expectedCash = computed(() => {
        const opening = activeSession.value?.opening_amount || 0
        const totalIn = inflows.value
            .filter(i => i.session_id === activeSession.value?.id)
            .reduce((sum, i) => sum + i.amount, 0)
        const totalOut = outflows.value
            .filter(o => o.session_id === activeSession.value?.id)
            .reduce((sum, o) => sum + o.amount, 0)
        return opening + totalIn - totalOut
    })

    const variance = computed(() => {
        if (countedAmount.value === null) return null
        return countedAmount.value - expectedCash.value
    })

    const sessionInflows = computed(() =>
        inflows.value.filter(i => i.session_id === activeSession.value?.id)
    )

    const sessionOutflows = computed(() =>
        outflows.value.filter(o => o.session_id === activeSession.value?.id)
    )

    function openSession(amount) {
        if (status.value !== CASH_SESSION_STATUS.CLOSED) return
        const session = {
            id: Date.now(),
            branch_id: 1,
            status: 'open',
            opened_by: 'cashier',
            opening_amount: Number(amount) || 0,
            expected_closing: null,
            counted_amount: null,
            variance: null,
            opened_at: new Date().toISOString(),
            closed_at: null,
        }
        activeSession.value = session
        openingAmount.value = session.opening_amount
        status.value = CASH_SESSION_STATUS.OPEN
        mock.cashSessions.unshift(session)
        ui.toastSuccess(`Cash session opened with Rs. ${amount.toLocaleString()}`)
    }

    function addInflow(entry) {
        if (!activeSession.value) return
        const item = {
            id: Date.now(),
            session_id: activeSession.value.id,
            category: entry.category || 'Sales',
            amount: Number(entry.amount),
            note: entry.note || '',
            created_at: new Date().toISOString(),
            actor: entry.actor || 'cashier',
        }
        inflows.value.push(item)
    }

    function addOutflow(entry) {
        if (!activeSession.value) return
        const item = {
            id: Date.now(),
            session_id: activeSession.value.id,
            category: entry.category || 'Expense',
            amount: Number(entry.amount),
            note: entry.note || '',
            created_at: new Date().toISOString(),
            actor: entry.actor || 'manager',
        }
        outflows.value.push(item)
    }

    function submitCount(counted) {
        if (status.value !== CASH_SESSION_STATUS.OPEN) return
        countedAmount.value = Number(counted)
        status.value = CASH_SESSION_STATUS.PENDING_COUNT
    }

    function confirmClose() {
        if (status.value !== CASH_SESSION_STATUS.PENDING_COUNT) return
        if (activeSession.value) {
            activeSession.value.status = 'closed'
            activeSession.value.counted_amount = countedAmount.value
            activeSession.value.variance = variance.value
            activeSession.value.closed_at = new Date().toISOString()
        }
        status.value = CASH_SESSION_STATUS.RECONCILED
        ui.toastSuccess('Cash session closed and reconciled')
    }

    function cancelCount() {
        status.value = CASH_SESSION_STATUS.OPEN
        countedAmount.value = null
    }

    return {
        activeSession, status, inflows, outflows,
        countedAmount, openingAmount,
        expectedCash, variance, sessionInflows, sessionOutflows,
        openSession, addInflow, addOutflow,
        submitCount, confirmClose, cancelCount,
    }
})
