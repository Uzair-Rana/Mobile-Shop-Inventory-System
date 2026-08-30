import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useMockDataStore } from './mockData'

export const useBranchStore = defineStore('branch', () => {
    const activeBranchId = ref(1)

    const branchList = computed(() => {
        const mock = useMockDataStore()
        return mock.branches
    })

    const activeBranch = computed(() => {
        const mock = useMockDataStore()
        return mock.branches.find(b => b.id === activeBranchId.value) || mock.branches[0] || null
    })

    function switchBranch(id) {
        activeBranchId.value = Number(id)
    }

    return { activeBranchId, branchList, activeBranch, switchBranch }
})
