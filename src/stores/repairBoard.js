/**
 * repairBoard store — kanban state for 10 repair stages.
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useMockDataStore } from './mockData'
import { useUiStore } from './ui'

export const REPAIR_COLUMNS = [
    { key: 'received', label: 'Received', badge: 'badge-blue' },
    { key: 'diagnosing', label: 'Diagnosing', badge: 'badge-yellow' },
    { key: 'awaiting_approval', label: 'Awaiting Approval', badge: 'badge-orange' },
    { key: 'waiting_parts', label: 'Waiting Parts', badge: 'badge-orange' },
    { key: 'in_repair', label: 'In Repair', badge: 'badge-purple' },
    { key: 'qc', label: 'QC Check', badge: 'badge-blue' },
    { key: 'repaired', label: 'Repaired', badge: 'badge-green' },
    { key: 'ready', label: 'Ready Pickup', badge: 'badge-green' },
    { key: 'unrepairable', label: 'Unrepairable', badge: 'badge-red' },
    { key: 'delivered', label: 'Delivered', badge: 'badge-gray' },
]

export const useRepairBoardStore = defineStore('repairBoard', () => {
    const mock = useMockDataStore()
    const ui = useUiStore()

    // Build columns keyed by status
    const columns = ref({})

    function loadBoard() {
        const cols = {}
        REPAIR_COLUMNS.forEach(c => { cols[c.key] = [] })
        mock.repairs.forEach(job => {
            const key = job.status
            if (cols[key]) {
                cols[key].push({ ...job })
            }
        })
        columns.value = cols
    }

    function moveJob(jobId, fromCol, toCol) {
        const from = columns.value[fromCol]
        const to = columns.value[toCol]
        if (!from || !to) return

        const idx = from.findIndex(j => j.id === Number(jobId))
        if (idx === -1) return

        const [job] = from.splice(idx, 1)
        job.status = toCol
        to.unshift(job)

        // Persist to mockData store
        mock.updateRepair(jobId, { status: toCol })
        mock.addRepairLog(jobId, {
            status: toCol,
            note: `Moved to ${toCol}`,
            updated_by_name: 'user',
        })

        ui.toastSuccess(`Job #${job.job_number} → ${toCol}`)
    }

    // Computed array for template iteration
    const columnList = computed(() =>
        REPAIR_COLUMNS.map(col => ({
            ...col,
            items: columns.value[col.key] || [],
        }))
    )

    // Initialize on store creation
    loadBoard()

    return { columns, columnList, loadBoard, moveJob }
})
