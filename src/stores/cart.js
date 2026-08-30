/**
 * POS Cart store — in-memory, no API calls.
 * Multi-tender payments, trade-in support.
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useMockDataStore } from './mockData'
import { useUiStore } from './ui'

export const useCartStore = defineStore('cart', () => {
    const mock = useMockDataStore()
    const ui = useUiStore()

    // ── State ──────────────────────────────────────────────────────────────────
    const items = ref([])
    const customer = ref(null)
    const notes = ref('')
    const tenders = ref([])       // [{ method, amount }]
    const tradeIn = ref(null)     // { imei, device_name, accepted_value }
    const invoiceDiscount = ref(0)
    const taxRate = ref(0)
    const submitting = ref(false)
    const lastInvoice = ref(null)

    // Legacy compat: single payment method for old code paths
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
        tradeIn.value ? (tradeIn.value.accepted_value || 0) : 0
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

    // ── Tender actions ─────────────────────────────────────────────────────────

    function addTender(method, amount) {
        tenders.value.push({ method, amount: Number(amount) || 0 })
    }

    function removeTender(idx) {
        tenders.value.splice(idx, 1)
    }

    function clearTenders() {
        tenders.value = []
    }

    function setTenderQuick(method, amount) {
        tenders.value = [{ method, amount: Number(amount) || grandTotal.value }]
    }

    // ── Trade-in ───────────────────────────────────────────────────────────────

    function setTradeIn(data) {
        tradeIn.value = data
    }

    function clearTradeIn() {
        tradeIn.value = null
    }

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

    // ── Checkout — purely in-memory ────────────────────────────────────────────

    async function checkout() {
        if (items.value.length === 0) {
            ui.toastWarn('Cart is empty')
            return null
        }
        submitting.value = true
        try {
            await new Promise(r => setTimeout(r, 150))

            const today = new Date().toISOString()
            const invNum = `INV-${String(mock.invoices.length + 1).padStart(4, '0')}`

            const lines = items.value.map((item, idx) => ({
                id: idx + 1,
                product_name: item.name,
                type: item.type,
                unit_id: item.unit_id,
                imei: item.imei || null,
                qty: item.qty,
                unit_price: item.price,
                discount_abs: item.discount_abs,
                discount_pct: item.discount_pct,
                line_total: item.price * item.qty - (item.discount_abs > 0 ? item.discount_abs : item.price * item.qty * item.discount_pct / 100),
            }))

            const invoice = {
                invoice_number: invNum,
                customer_id: customer.value?.id || null,
                customer_name: customer.value?.name || null,
                status: 'paid',
                payment_method: tenders.value.length === 1 ? tenders.value[0].method : 'split',
                grand_total: grandTotal.value,
                subtotal: subtotal.value,
                tax_amount: taxAmount.value,
                invoice_discount: invoiceDiscount.value,
                amount_paid: Math.min(totalTendered.value, grandTotal.value),
                balance_due: remainingDue.value,
                change_amount: changeAmount.value,
                amount_received: totalTendered.value,
                created_at: today,
                line_count: lines.length,
            }

            const saved = mock.addInvoice(invoice)
            mock.addInvoiceLines(saved.id, lines)

            // Update device lifecycle states
            items.value
                .filter(i => i.type === 'unit')
                .forEach(i => {
                    mock.updateDevice(i.product_id, { lifecycle_state: 'sold' })
                })

            lastInvoice.value = { ...saved, lines }
            const result = lastInvoice.value
            clearCart()
            return result
        } catch (e) {
            ui.toastError('Checkout failed')
            throw e
        } finally {
            submitting.value = false
        }
    }

    return {
        items, customer, notes, tenders, tradeIn,
        invoiceDiscount, taxRate, submitting, lastInvoice,
        // Legacy compat
        paymentMethod, amountReceived,
        // Computed
        subtotal, taxAmount, grandTotal,
        totalTendered, remainingDue, changeAmount,
        tradeInValue, itemCount,
        // Actions
        addItem, removeItem, updateQty, updatePrice, updateDiscount,
        addTender, removeTender, clearTenders, setTenderQuick,
        setTradeIn, clearTradeIn,
        setCustomer, clearCustomer, clearCart, checkout,
    }
})
