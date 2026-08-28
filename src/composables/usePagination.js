/**
 * usePagination — DRF-compatible pagination helper.
 * Works with DRF's default PageNumberPagination (page, page_size)
 * or cursor-based (next/previous URLs).
 */
import { ref, computed } from 'vue'

export function usePagination({ pageSize = 20 } = {}) {
    const currentPage = ref(1)
    const totalCount = ref(0)
    const _pageSize = ref(pageSize)

    const totalPages = computed(() => Math.ceil(totalCount.value / _pageSize.value) || 1)
    const hasNext = computed(() => currentPage.value < totalPages.value)
    const hasPrev = computed(() => currentPage.value > 1)

    /** Returns params to pass to the API */
    const queryParams = computed(() => ({
        page: currentPage.value,
        page_size: _pageSize.value,
    }))

    function setFromResponse(data) {
        totalCount.value = data.count ?? 0
    }

    function goTo(page) {
        currentPage.value = Math.max(1, Math.min(page, totalPages.value))
    }

    function next() { if (hasNext.value) currentPage.value++ }
    function prev() { if (hasPrev.value) currentPage.value-- }
    function reset() { currentPage.value = 1 }

    return {
        currentPage, totalCount, pageSize: _pageSize, totalPages,
        hasNext, hasPrev, queryParams,
        setFromResponse, goTo, next, prev, reset,
    }
}
