/**
 * useAging — compute overdue aging buckets from installment plans.
 * Buckets: 1-7d, 8-30d, 31-60d, 61-90d, 90d+
 */
import { computed } from 'vue'

const BUCKETS = [
    { label: '1–7 days', min: 1, max: 7 },
    { label: '8–30 days', min: 8, max: 30 },
    { label: '31–60 days', min: 31, max: 60 },
    { label: '61–90 days', min: 61, max: 90 },
    { label: '90+ days', min: 91, max: Infinity },
]

export function useAging(plansRef) {
    const buckets = computed(() => {
        const now = Date.now()
        return BUCKETS.map(bucket => {
            const plans = (plansRef.value || []).filter(p => {
                if (!['overdue', 'defaulted'].includes(p.status)) return false
                if (!p.next_due_date) return false
                const daysOverdue = Math.floor((now - new Date(p.next_due_date).getTime()) / (1000 * 60 * 60 * 24))
                return daysOverdue >= bucket.min && daysOverdue <= bucket.max
            })
            const totalAmount = plans.reduce((sum, p) => sum + (p.remaining_amount || 0), 0)
            return {
                ...bucket,
                count: plans.length,
                totalAmount,
                plans,
            }
        })
    })

    return { buckets }
}
