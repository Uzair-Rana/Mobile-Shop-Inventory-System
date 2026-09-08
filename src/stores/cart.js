/**
 * POS Cart store — uses real salesApi for checkout.
 * Multi-tender payments and trade-in support.
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { salesApi } from '@/api/sales'
import { useUiStore } from './ui'

export const useCartStore = defineStore('cart', () => {
    const ui = useUiStore()

    // ── State ──────────────────────────────────────────────────────────────────
    const items = ref([])
    const customer = ref(null)
    const notes = ref('')
    const tenders = ref([])           // [{ method, amount }]
    const tradeIn = ref(null)         // { unit_id, imei, device_name, accepted_value }
    const invoiceDiscount = ref(0)
    const taxRate = ref(0)
    const submitting = ref(false)
    const lastInvoice = ref(null)

    // Legacy compat
    const paymentMethod = computed(() => tenders.value[0]?.method || 'cash')
    const amountReceived = computed(() => totalTendered.value)

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

    const tradeInValue = computed(() =>
        tradeIn.value ? (Number(tradeIn.value.accepted_value) || 0) : 0
    )

    const grandTotal = computed(() =>
        Math.max(0, subtotal.value + taxAmount.value - invoiceDiscount.value - tradeInValue.value)
    )

    const totalTendered = computed(() =>
        tenders.value.reduce((sum, t) => sum + (Number(t.amount) || 0), 0)
    )

    const remainingDue = computed(() =>
        Math.max(0, grandTotal.value - totalTendered.value)
    )

    const changeAmount = computed(() =>
        Math.max(0, totalTendered.value - grandTotal.value)
    )

    const itemCount = computed(() =>
        items.value.reduce((n, i) => n + i.qty, 0)
    )

    // ── Item actions ───────────────────────────────────────────────────────────

    function addItem(product) {
        if (product.imei) {
            const exists = items.value.find(i => i.imei === product.imei)
            if (exists) { ui.toastWarn?.(`IMEI ${product.imei} already in cart`); return }
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

    function removeItem(id) { items.value = items.value.filter(i => i.id !== id) }

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

    // ── Tender actions ─────────────────────────────────────────────────────────

    function addTender(method, amount) { tenders.value.push({ method, amount: Number(amount) || 0 }) }
    function removeTender(idx) { tenders.value.splice(idx, 1) }
    function clearTenders() { tenders.value = [] }
    function setTenderQuick(method, amount) {
        tenders.value = [{ method, amount: Number(amount) || grandTotal.value }]
    }

    // ── Trade-in ───────────────────────────────────────────────────────────────

    function setTradeIn(data) { tradeIn.value = data }
    function clearTradeIn() { tradeIn.value = null }

    // ── Customer ───────────────────────────────────────────────────────────────

    function setCustomer(c) { customer.value = c }
    function clearCustomer() { customer.value = null }

    function clearCart() {
        items.value = []
        customer.value = null
        notes.value = ''
        tenders.value = []
        tradeIn.value = null
        invoiceDiscount.value = 0
        lastInvoice.value = null
    }

    // ── Checkout — calls Django backend ───────────────────────────────────────

    async function checkout() {
        if (items.value.length === 0) {
            ui.toastWarn?.('Cart is empty')
            return null
        }
        submitting.value = true
        try {
            // Build DRF-compatible payload
            const lines = items.value.map(item => {
                const lineTotal = item.price * item.qty
                const disc = item.discount_abs > 0
                    ? item.discount_abs
                    : lineTotal * (item.discount_pct / 100)
                return {
                    product_type: item.type === 'unit' ? 'unit' : 'accessory',
                    product_id: item.unit_id || item.product_id,
                    product_name: item.name,
                    sku: item.sku || '',
                    imei: item.imei || '',
                    qty: item.qty,
                    unit_price: item.price.toFixed(2),
                    discount: disc.toFixed(2),
                    line_total: (lineTotal - disc).toFixed(2),
                }
            })

            const payload = {
                customer: customer.value?.id || null,
                customer_name: customer.value?.name || 'Walk-in',
                status: remainingDue.value <= 0 ? 'paid' : 'partially_paid',
                payment_method: tenders.value.length === 1 ? tenders.value[0].method : 'cash',
                subtotal: subtotal.value.toFixed(2),
                discount_amount: invoiceDiscount.value.toFixed(2),
                tax_amount: taxAmount.value.toFixed(2),
                trade_in_value: tradeInValue.value.toFixed(2),
                trade_in_unit_id: tradeIn.value?.unit_id || null,
                grand_total: grandTotal.value.toFixed(2),
                amount_paid: Math.min(totalTendered.value, grandTotal.value).toFixed(2),
                notes: notes.value,
                lines,
            }

            // Create the invoice
            const { data: invoice } = await salesApi.createInvoice(payload)

            // Finalize it immediately (draft → finalized)
            const { data: finalized } = await salesApi.finalizeInvoice(invoice.id)

            // Record each tender as a separate payment if split
            if (tenders.value.length > 1) {
                for (const tender of tenders.value) {
                    await salesApi.addPayment(invoice.id, {
                        amount: tender.amount.toFixed(2),
                        method: tender.method,
                    })
                }
            }

            lastInvoice.value = finalized
            clearCart()
            return finalized

        } catch (e) {
            ui.toastError?.('Checkout failed: ' + (e.displayMessage || e.message))
            throw e
        } finally {
            submitting.value = false
        }
    }

    return {
        items, customer, notes, tenders, tradeIn,
        invoiceDiscount, taxRate, submitting, lastInvoice,
        paymentMethod, amountReceived,
        subtotal, taxAmount, grandTotal,
        totalTendered, remainingDue, changeAmount,
        tradeInValue, itemCount,
        addItem, removeItem, updateQty, updatePrice, updateDiscount,
        addTender, removeTender, clearTenders, setTenderQuick,
        setTradeIn, clearTradeIn,
        setCustomer, clearCustomer, clearCart, checkout,
    }
})
