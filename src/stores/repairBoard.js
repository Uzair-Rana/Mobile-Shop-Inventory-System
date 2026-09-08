/**
 * repairBoard store — kanban state for repair stages.
 * Loads from real API via repairsApi.getBoard()
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { repairsApi } from '@/api/repairs'
import { useUiStore } from './ui'

export const REPAIR_COLUMNS = [
    { key: 'received', label: 'Received', badge: 'badge-blue' },
    { key: 'diagnosed', label: 'Diagnosed', badge: 'badge-blue' },
    { key: 'waiting_parts', label: 'Waiting Parts', badge: 'badge-orange' },
    { key: 'in_progress', label: 'In Repair', badge: 'badge-purple' },
    { key: 'ready', label: 'Ready Pickup', badge: 'badge-green' },
    { key: 'unrepairable', label: 'Unrepairable', badge: 'badge-red' },
    { key: 'cancelled', label: 'Cancelled', badge: 'badge-gray' },
]

export const useRepairBoardStore = defineStore('repairBoard', () => {
    const ui = useUiStore()

    const columns = ref({})
    const loading = ref(false)

    async function loadBoard() {
        loading.value = true
        try {
            const { data } = await repairsApi.getBoard()
            // API returns { received: [...], diagnosed: [...], ... }
            const cols = {}
            REPAIR_COLUMNS.forEach(c => { cols[c.key] = data[c.key] || [] })
            columns.value = cols
        } catch (e) {
            console.error('[RepairBoard] Failed to load:', e)
            // Seed empty columns so UI doesn't crash
            const cols = {}
            REPAIR_COLUMNS.forEach(c => { cols[c.key] = [] })
            columns.value = cols
        } finally {
            loading.value = false
        }
    }

    async function moveJob(jobId, fromCol, toCol) {
        const from = columns.value[fromCol]
        const to = columns.value[toCol]
        if (!from || !to) return

        const idx = from.findIndex(j => j.id === Number(jobId))
        if (idx === -1) return

        // Optimistic update
        const [job] = from.splice(idx, 1)
        job.status = toCol
        to.unshift(job)

        try {
            await repairsApi.updateStatus(jobId, { status: toCol })
            ui.toastSuccess?.(`Job #${job.job_number} → ${toCol}`)
        } catch (e) {
            // Rollback
            to.splice(to.indexOf(job), 1)
            from.splice(idx, 0, job)
            ui.toastError?.('Failed to move job: ' + (e.displayMessage || e.message))
        }
    }

    const columnList = computed(() =>
        REPAIR_COLUMNS.map(col => ({
            ...col,
            items: columns.value[col.key] || [],
        }))
    )

    return { columns, columnList, loading, loadBoard, moveJob }
})
