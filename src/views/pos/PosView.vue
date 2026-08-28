<script setup>
/**
 * PosView — full-screen Point of Sale screen.
 * Keyboard-first, scanner-friendly. No AppShell wrapper — uses its own layout.
 * Sync indicator is always visible in the POS header.
 */
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useCartStore } from '@/stores/cart'
import { useInventoryStore } from '@/stores/inventory'
import { useUiStore } from '@/stores/ui'
import { usePermissions } from '@/composables/usePermissions'
import { PAYMENT_METHODS } from '@/utils/constants'
import { formatMoney } from '@/utils/money'
import { customersApi } from '@/api/customers'

import ScannerInput from '@/components/pos/ScannerInput.vue'
import CartItem from '@/components/pos/CartItem.vue'
import CartTotals from '@/components/pos/CartTotals.vue'
import MoneyDisplay from '@/components/ui/MoneyDisplay.vue'
import AppBadge from '@/components/ui/AppBadge.vue'
import AppButton from '@/components/ui/AppButton.vue'
import AppSelect from '@/components/ui/AppSelect.vue'
import SyncIndicator from '@/components/layout/SyncIndicator.vue'
import { useConfirm } from '@/composables/useConfirm'

const cart     = useCartStore()
const inv      = useInventoryStore()
const ui       = useUiStore()
const router   = useRouter()
const perms    = usePermissions()
const { confirm } = useConfirm()

const scannerRef      = ref(null)
const scanning        = ref(false)
const scanError       = ref('')
const customerSearch  = ref('')
const customerResults = ref([])
const showReceipt     = ref(false)
const lastInvoice     = ref(null)

// ── Scanner handler ────────────────────────────────────────────────────────────
async function handleScan(value) {
  scanError.value = ''
  scanning.value  = true
  try {
    const result = await inv.scanItem(value)
    if (!result) {
      scanError.value = `"${value}" not found in inventory`
      ui.toastWarn(`Product not found: ${value}`)
      return
    }
    cart.addItem(result)
  } catch (e) {
    scanError.value = e.displayMessage || `Lookup failed for "${value}"`
  } finally {
    scanning.value = false
  }
}

// ── Customer search ────────────────────────────────────────────────────────────
let customerTimer = null
async function searchCustomer() {
  if (customerSearch.value.length < 2) { customerResults.value = []; return }
  clearTimeout(customerTimer)
  customerTimer = setTimeout(async () => {
    const res = await customersApi.search(customerSearch.value)
    customerResults.value = res.data.results ?? res.data
  }, 250)
}

function selectCustomer(c) {
  cart.setCustomer(c)
  customerSearch.value  = c.name
  customerResults.value = []
}

function clearCustomer() {
  cart.clearCustomer()
  customerSearch.value = ''
}

// ── Checkout ──────────────────────────────────────────────────────────────────
async function handleCheckout() {
  if (cart.items.length === 0) {
    ui.toastWarn('Cart is empty')
    return
  }

  const ok = await confirm({
    title:        'Confirm Sale',
    message:      `Complete sale of ${cart.itemCount} item(s) for ${formatMoney(cart.grandTotal)}?`,
    effect:       `Payment: ${cart.paymentMethod} · ${cart.customer ? cart.customer.name : 'Walk-in customer'}`,
    confirmLabel: 'Complete Sale',
    confirmClass: 'btn-primary',
  })
  if (!ok) return

  try {
    const invoice = await cart.checkout()
    lastInvoice.value = invoice
    showReceipt.value = true
    scannerRef.value?.focus()
  } catch { /* cart.checkout already shows toast */ }
}

function closeReceipt() {
  showReceipt.value = false
  lastInvoice.value = null
  scannerRef.value?.focus()
}

function newSale() {
  cart.clearCart()
  closeReceipt()
}
</script>

<template>
  <div class="h-screen flex flex-col bg-gray-100 overflow-hidden">
    <!-- POS Top bar -->
    <div class="bg-gray-900 text-white h-11 flex items-center px-4 gap-4 shrink-0">
      <button
        class="text-gray-400 hover:text-white transition-colors"
        aria-label="Back to dashboard"
        @click="router.push('/dashboard')"
      >
        ← Back
      </button>
      <span class="font-semibold text-sm flex-1">DEVNEST · Point of Sale</span>
      <SyncIndicator />
    </div>

    <!-- Main POS layout: left=product search, right=cart -->
    <div class="flex-1 flex overflow-hidden">

      <!-- ── LEFT: Scanner + search results ─────────────────────────────── -->
      <div class="flex-1 flex flex-col p-3 gap-3 overflow-hidden">
        <!-- Scanner input (always focused) -->
        <ScannerInput
          ref="scannerRef"
          :disabled="cart.submitting"
          @scan="handleScan"
        />

        <!-- Scan feedback -->
        <div
          v-if="scanError"
          class="text-xs text-red-600 bg-red-50 border border-red-200 rounded px-3 py-2"
          role="alert"
        >
          {{ scanError }}
        </div>

        <!-- Customer selector -->
        <div class="card p-3">
          <p class="label mb-1">Customer</p>
          <div class="relative">
            <input
              v-model="customerSearch"
              type="text"
              class="input text-sm"
              placeholder="Search by name or phone…"
              autocomplete="off"
              data-no-scanner-refocus
              @input="searchCustomer"
            />
            <!-- Customer selected badge -->
            <div v-if="cart.customer" class="absolute inset-0 flex items-center px-3 bg-white rounded-md border border-blue-300">
              <span class="flex-1 text-sm text-blue-800 font-medium">{{ cart.customer.name }}</span>
              <button class="text-gray-400 hover:text-red-500 ml-2" @click="clearCustomer" data-no-scanner-refocus>✕</button>
            </div>
            <!-- Dropdown results -->
            <div
              v-if="customerResults.length > 0"
              class="absolute z-10 left-0 right-0 top-full mt-1 card shadow-lg py-1 max-h-48 overflow-y-auto"
            >
              <button
                v-for="c in customerResults"
                :key="c.id"
                class="w-full text-left px-3 py-2 text-sm hover:bg-gray-50 flex items-center justify-between"
                data-no-scanner-refocus
                @click="selectCustomer(c)"
              >
                <span>{{ c.name }}</span>
                <span class="text-gray-400 text-xs">{{ c.phone }}</span>
              </button>
            </div>
          </div>
        </div>

        <!-- Notes -->
        <div class="card p-3">
          <p class="label mb-1">Note</p>
          <input
            v-model="cart.notes"
            type="text"
            class="input text-sm"
            placeholder="Optional sale note…"
            data-no-scanner-refocus
          />
        </div>
      </div>

      <!-- ── RIGHT: Cart ─────────────────────────────────────────────────── -->
      <div class="w-96 bg-white border-l border-gray-200 flex flex-col overflow-hidden">
        <!-- Cart header -->
        <div class="px-4 py-3 border-b border-gray-100 flex items-center justify-between shrink-0">
          <span class="font-semibold text-gray-900">
            Cart
            <span v-if="cart.itemCount > 0" class="text-gray-500 text-sm font-normal ml-1">({{ cart.itemCount }})</span>
          </span>
          <button
            v-if="cart.items.length > 0"
            class="text-xs text-red-500 hover:text-red-700"
            data-no-scanner-refocus
            @click="cart.clearCart()"
          >
            Clear all
          </button>
        </div>

        <!-- Line items -->
        <div class="flex-1 overflow-y-auto px-4 py-2">
          <CartItem
            v-for="item in cart.items"
            :key="item.id"
            :item="item"
          />
          <div
            v-if="cart.items.length === 0"
            class="flex flex-col items-center justify-center h-full text-gray-400 text-sm py-12"
          >
            <svg class="w-12 h-12 mb-3 opacity-30" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 3h1.386c.51 0 .955.343 1.087.835l.383 1.437M7.5 14.25a3 3 0 00-3 3h15.75m-12.75-3h11.218c1.121-2.3 2.1-4.684 2.924-7.138a60.114 60.114 0 00-16.536-1.84M7.5 14.25L5.106 5.272M6 20.25a.75.75 0 11-1.5 0 .75.75 0 011.5 0zm12.75 0a.75.75 0 11-1.5 0 .75.75 0 011.5 0z"/>
            </svg>
            <p>Scan or search to add items</p>
          </div>
        </div>

        <!-- Totals + payment -->
        <div class="shrink-0 border-t border-gray-100 px-4 py-3 bg-gray-50 space-y-3">
          <!-- Invoice-level discount (manager only) -->
          <div v-if="perms.canManageDiscounts.value" class="flex items-center gap-2 text-sm">
            <label class="text-gray-600 whitespace-nowrap">Invoice Disc.</label>
            <input
              v-model.number="cart.invoiceDiscount"
              type="number"
              min="0"
              step="100"
              class="input text-right money text-sm"
              placeholder="0"
              data-no-scanner-refocus
            />
          </div>

          <!-- Payment method -->
          <div class="flex items-center gap-2 text-sm">
            <label class="text-gray-600 whitespace-nowrap">Pay via</label>
            <select
              v-model="cart.paymentMethod"
              class="input text-sm"
              data-no-scanner-refocus
            >
              <option v-for="m in PAYMENT_METHODS" :key="m.value" :value="m.value">{{ m.label }}</option>
            </select>
          </div>

          <CartTotals />

          <!-- Checkout button -->
          <AppButton
            variant="primary"
            size="lg"
            :loading="cart.submitting"
            :disabled="cart.items.length === 0"
            class="w-full"
            data-no-scanner-refocus
            @click="handleCheckout"
          >
            Complete Sale · <MoneyDisplay :value="cart.grandTotal" />
          </AppButton>
        </div>
      </div>
    </div>

    <!-- ── Receipt modal ──────────────────────────────────────────────────── -->
    <Teleport to="body">
      <div
        v-if="showReceipt"
        class="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4"
      >
        <div class="card w-80 shadow-2xl p-6 text-center space-y-4">
          <div class="h-14 w-14 rounded-full bg-green-100 flex items-center justify-center mx-auto">
            <svg class="w-7 h-7 text-green-600" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75l6 6 9-13.5"/>
            </svg>
          </div>
          <div>
            <h3 class="text-lg font-bold text-gray-900">Sale Complete</h3>
            <p class="text-sm text-gray-500 mt-1">Invoice #{{ lastInvoice?.invoice_number }}</p>
          </div>
          <div class="bg-gray-50 rounded-lg p-3 text-left space-y-1 text-sm">
            <div class="flex justify-between">
              <span class="text-gray-500">Total</span>
              <MoneyDisplay :value="lastInvoice?.grand_total" class="font-semibold" />
            </div>
            <div class="flex justify-between">
              <span class="text-gray-500">Received</span>
              <MoneyDisplay :value="lastInvoice?.amount_received" />
            </div>
            <div class="flex justify-between text-green-700 font-semibold">
              <span>Change</span>
              <MoneyDisplay :value="lastInvoice?.change_amount" />
            </div>
          </div>
          <div class="flex gap-2">
            <AppButton variant="secondary" class="flex-1" @click="closeReceipt">Close</AppButton>
            <AppButton variant="primary" class="flex-1" @click="newSale">New Sale</AppButton>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>
