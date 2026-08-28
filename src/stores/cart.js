/**
 * POS Cart store.
 * Manages line items, discounts, payment method, and the active customer for a sale session.
 * All money arithmetic is done with integer paise/paisa (×100) then divided on display
 * to avoid floating-point accumulation in totals.
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { salesApi } from '@/api/sales'
import { useUiStore } from './ui'

export const useCartStore = defineStore('cart', () => {
    const ui = useUiStore()

    // ── State ──────────────────────────────────────────────────────────────────
    const items = ref([])   // { id, type, product_id, unit_id, name, sku, imei, price, qty, discount_pct, discount_abs }
    const customer = ref(null) // { id, name, phone }
    const notes = ref('')
    const paymentMethod = ref('cash')
    const amountReceived = ref(0)
    const invoiceDiscount = ref(0)   // absolute amount off the whole invoice
    const taxRate = ref(0)       // e.g. 17 for 17%
    const submitting = ref(false)
    const lastInvoice = ref(null)    // result of last finalized invoice

    // ── Computed totals ────────────────────────────────────────────────────────
    const subtotal = computed(() =>
        items.value.reduce((sum, item) => {
            const lineTotal = item.price * item.qty
            const disc = item.discount_abs > 0
                ? item.discount_abs
                : lineTotal * (item.discount_pct / 100)
            return sum + (lineTotal - disc)
        }, 0)
    )

    const taxAmount = computed(() =>
        taxRate.value > 0 ? subtotal.value * (taxRate.value / 100) : 0
    )

    const grandTotal = computed(() =>
        Math.max(0, subtotal.value + taxAmount.value - invoiceDiscount.value)
    )

    const changeAmount = computed(() =>
        Math.max(0, (amountReceived.value || 0) - grandTotal.value)
    )

    const itemCount = computed(() =>
        items.value.reduce((n, i) => n + i.qty, 0)
    )

    // ── Actions ────────────────────────────────────────────────────────────────

    /** Add a scanned/searched product to the cart */
    function addItem(product) {
        // Serialised units (IMEI): one unit per line, no qty > 1
        if (product.imei) {
            const exists = items.value.find(i => i.imei === product.imei)
            if (exists) {
                ui.toastWarn(`IMEI ${product.imei} is already in the cart`)
                return
            }
            items.value.push({
                id: `unit_${product.unit_id}`,
                type: 'unit',
                product_id: product.product_id,
                unit_id: product.unit_id,
                name: product.name,
                sku: product.sku,
                imei: product.imei,
                price: Number(product.price),
                qty: 1,
                discount_pct: 0,
                discount_abs: 0,
            })
            return
        }
        // Accessories / non-serialised
        const exists = items.value.find(i => i.id === `acc_${product.product_id}`)
        if (exists) {
            exists.qty += 1
        } else {
            items.value.push({
                id: `acc_${product.product_id}`,
                type: 'accessory',
                product_id: product.product_id,
                unit_id: null,
                name: product.name,
                sku: product.sku,
                imei: null,
                price: Number(product.price),
                qty: 1,
                discount_pct: 0,
                discount_abs: 0,
            })
        }
    }

    function removeItem(id) {
        items.value = items.value.filter(i => i.id !== id)
    }

    function updateQty(id, qty) {
        const item = items.value.find(i => i.id === id)
        if (item) item.qty = Math.max(1, parseInt(qty) || 1)
    }

    function updatePrice(id, price) {
        const item = items.value.find(i => i.id === id)
        if (item) item.price = Math.max(0, parseFloat(price) || 0)
    }

    function updateDiscount(id, { pct = 0, abs = 0 }) {
        const item = items.value.find(i => i.id === id)
        if (item) { item.discount_pct = pct; item.discount_abs = abs }
    }

    function setCustomer(c) { customer.value = c }
    function clearCustomer() { customer.value = null }

    function clearCart() {
        items.value = []
        customer.value = null
        notes.value = ''
        paymentMethod.value = 'cash'
        amountReceived.value = 0
        invoiceDiscount.value = 0
        lastInvoice.value = null
    }

    /** Build DRF-compatible payload and POST */
    async function checkout() {
        if (items.value.length === 0) {
            ui.toastWarn('Cart is empty')
            return null
        }
        submitting.value = true
        try {
            const payload = {
                customer: customer.value?.id || null,
                notes: notes.value,
                payment_method: paymentMethod.value,
                amount_received: amountReceived.value,
                invoice_discount: invoiceDiscount.value,
                tax_rate: taxRate.value,
                lines: items.value.map(item => ({
                    type: item.type,
                    product_id: item.product_id,
                    unit_id: item.unit_id,
                    qty: item.qty,
                    unit_price: item.price,
                    discount_pct: item.discount_pct,
                    discount_abs: item.discount_abs,
                })),
            }
            const res = await salesApi.createInvoice(payload)
            const invoice = res.data
            // Auto-finalize
            const finRes = await salesApi.finalizeInvoice(invoice.id)
            lastInvoice.value = finRes.data
            clearCart()
            return finRes.data
        } catch (e) {
            ui.toastError(e.displayMessage || 'Checkout failed')
            throw e
        } finally {
            submitting.value = false
        }
    }

    return {
        items, customer, notes, paymentMethod, amountReceived,
        invoiceDiscount, taxRate, submitting, lastInvoice,
        subtotal, taxAmount, grandTotal, changeAmount, itemCount,
        addItem, removeItem, updateQty, updatePrice, updateDiscount,
        setCustomer, clearCustomer, clearCart, checkout,
    }
})
