/**
 * useStepUpAuth — requires re-authentication for sensitive actions.
 */
import { useUiStore } from '@/stores/ui'

export function useStepUpAuth() {
    const ui = useUiStore()

    function requireStepUp(action) {
        return ui.requireStepUp(action)
    }

    return { requireStepUp }
}
