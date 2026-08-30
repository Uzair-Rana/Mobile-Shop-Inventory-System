/**
 * useBranch — thin wrapper over branchStore.
 */
import { useBranchStore } from '@/stores/branch'

export function useBranch() {
    const store = useBranchStore()
    return {
        activeBranch: store.activeBranch,
        activeBranchId: store.activeBranchId,
        branchList: store.branchList,
        switchBranch: store.switchBranch,
    }
}
