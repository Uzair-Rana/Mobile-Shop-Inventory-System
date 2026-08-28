/**
 * useConfirm — programmatic confirmation dialog.
 * Destructive actions MUST pass `effect` describing financial/inventory impact.
 *
 * Usage:
 *   const { confirm } = useConfirm()
 *   const ok = await confirm({
 *     title: 'Void Invoice #1023',
 *     message: 'This will cancel the sale.',
 *     effect: 'Restocks 2 units and refunds Rs. 45,000 to the customer.',
 *     confirmLabel: 'Void Invoice',
 *   })
 *   if (ok) { ... }
 */
import { useUiStore } from '@/stores/ui'

export function useConfirm() {
    const ui = useUiStore()
    return { confirm: ui.confirm }
}
