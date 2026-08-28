/**
 * useScanner — keyboard-first barcode/IMEI scanner composable.
 *
 * Scanners send rapid keystrokes + Enter (or a configurable terminator).
 * This composable captures those events on a given input ref, distinguishes
 * scanner input (rapid succession) from human typing, and fires onScan(value).
 *
 * Usage:
 *   const { inputRef, inputValue, isScannerActive } = useScanner({ onScan })
 *   <input ref="inputRef" v-model="inputValue" />
 *
 * The component can also just call handleKeydown directly if it manages its own input.
 */
import { ref, onMounted, onUnmounted } from 'vue'

const SCANNER_SPEED_MS = 50  // keystrokes faster than this are scanner-like
const MIN_SCAN_LENGTH = 4   // minimum chars to consider a scan valid

export function useScanner({ onScan, terminator = 'Enter', autoFocus = true } = {}) {
    const inputRef = ref(null)
    const inputValue = ref('')
    const isScannerActive = ref(false)

    let lastKeyTime = 0
    let scanBuffer = ''
    let scanTimer = null

    function handleKeydown(e) {
        const now = Date.now()
        const elapsed = now - lastKeyTime
        lastKeyTime = now

        if (e.key === terminator) {
            e.preventDefault()
            const value = scanBuffer || inputValue.value
            if (value.length >= MIN_SCAN_LENGTH) {
                isScannerActive.value = true
                onScan?.(value.trim())
                setTimeout(() => { isScannerActive.value = false }, 300)
            }
            scanBuffer = ''
            inputValue.value = ''
            clearTimeout(scanTimer)
            return
        }

        // Accumulate scanner buffer (rapid keystrokes)
        if (elapsed < SCANNER_SPEED_MS && e.key.length === 1) {
            scanBuffer += e.key
        } else {
            // Human-typed: clear scanner buffer, let v-model handle the input normally
            scanBuffer = ''
        }

        // Reset buffer if typing slows down (human pause)
        clearTimeout(scanTimer)
        scanTimer = setTimeout(() => { scanBuffer = '' }, 500)
    }

    /** Call this to programmatically focus the scanner input (e.g. after a modal closes) */
    function refocus() {
        inputRef.value?.focus()
    }

    onMounted(() => {
        if (autoFocus && inputRef.value) inputRef.value.focus()
    })

    onUnmounted(() => { clearTimeout(scanTimer) })

    return { inputRef, inputValue, isScannerActive, handleKeydown, refocus }
}
