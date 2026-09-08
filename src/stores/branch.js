import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { branchesApi } from '@/api/branches'

export const useBranchStore = defineStore('branch', () => {
    const branches = ref([])
    const activeBranchId = ref(
        Number(localStorage.getItem('devnest_branch_id')) || null
    )
    const loading = ref(false)

    const activeBranch = computed(() =>
        branches.value.find(b => b.id === activeBranchId.value) || branches.value[0] || null
    )

    const branchList = computed(() => branches.value)

    async function fetchBranches() {
        loading.value = true
        try {
            const { data } = await branchesApi.list()
            // DRF returns paginated { results: [] } or plain array
            branches.value = Array.isArray(data) ? data : (data.results || [])

            // Set default branch if none active yet
            if (!activeBranchId.value && branches.value.length) {
                const defaultBranch = branches.value.find(b => b.is_default) || branches.value[0]
                switchBranch(defaultBranch.id)
            }
        } catch (e) {
            console.error('[BranchStore] Failed to load branches:', e)
        } finally {
            loading.value = false
        }
    }

    function switchBranch(id) {
        activeBranchId.value = Number(id)
        localStorage.setItem('devnest_branch_id', String(id))
    }

    return {
        branches, activeBranchId, activeBranch, branchList, loading,
        fetchBranches, switchBranch,
    }
})
