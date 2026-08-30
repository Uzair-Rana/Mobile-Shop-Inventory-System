/**
 * useChartData — chart + table view toggle helper.
 */
import { ref, computed } from 'vue'

export function useChartData(dataFn, options = {}) {
    const view = ref('chart') // 'chart' | 'table'
    const rawData = computed(() => dataFn())

    const chartData = computed(() => {
        if (options.transform) return options.transform(rawData.value)
        return rawData.value
    })

    function toggleView() {
        view.value = view.value === 'chart' ? 'table' : 'chart'
    }

    return { view, rawData, chartData, toggleView }
}
