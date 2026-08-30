/**
 * usePrint — programmatic print with layout support.
 */
import { ref } from 'vue'

export function usePrint() {
    const printRef = ref(null)

    function print(layout = '80mm') {
        if (printRef.value?.print) {
            printRef.value.print(layout)
        } else {
            window.print()
        }
    }

    return { printRef, print }
}
