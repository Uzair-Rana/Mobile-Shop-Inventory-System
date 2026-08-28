<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { purchasesApi } from '@/api/purchases'
import { suppliersApi } from '@/api/suppliers'
import { inventoryApi } from '@/api/inventory'
import { useUiStore } from '@/stores/ui'
import { formatMoney } from '@/utils/money'
import AppInput from '@/components/ui/AppInput.vue'
import AppButton from '@/components/ui/AppButton.vue'
import MoneyDisplay from '@/components/ui/MoneyDisplay.vue'

const router    = useRouter()
const ui        = useUiStore()
const saving    = ref(false)
const suppliers = ref([])
const products  = ref([])

const form = ref({
  supplier: '',
  expected_delivery: '',
  notes: '',
  lines: [],
})

const newLine = ref({ product: '', qty: 1, unit_cost: 0, imei_list: '' })
const total = computed(() => form.value.lines.reduce((s, l) => s + l.qty * l.unit_cost, 0))

onMounted(async () => {
  const [sRes, pRes] = await Promise.all([
    suppliersApi.listSuppliers({ page_size: 100 }),
    inventoryApi.listProducts({ page_size: 200 }),
  ])
  suppliers.value = sRes.data.results ?? sRes.data
  products.value  = pRes.data.results ?? pRes.data
})

function addLine() {
  if (!newLine.value.product || !newLine.value.qty) return
  const product = products.value.find(p => p.id == newLine.value.product)
  form.value.lines.push({
    product:   newLine.value.product,
    product_name: product?.name || '',
    qty:       Number(newLine.value.qty),
    unit_cost: Number(newLine.value.unit_cost),
    imei_list: newLine.value.imei_list,
  })
  newLine.value = { product: '', qty: 1, unit_cost: 0, imei_list: '' }
}

function removeLine(i) { form.value.lines.splice(i, 1) }

async function handleSubmit() {
  if (!form.value.supplier) { ui.toastWarn('Select a supplier'); return }
  if (form.value.lines.length === 0) { ui.toastWarn('Add at least one line item'); return }
  saving.value = true
  try {
    const res = await purchasesApi.createOrder(form.value)
    ui.toastSuccess('Purchase order created')
    router.push(`/purchases/orders/${res.data.id}`)
  } catch (e) {
    ui.toastError(e.displayMessage || 'Failed to create PO')
  } finally { saving.value = false }
}
</script>

<template>
  <div class="max-w-3xl space-y-6">
    <div class="flex items-center justify-between">
      <h2 class="text-lg font-semibold text-gray-900">New Purchase Order</h2>
      <AppButton variant="ghost" @click="router.back()">← Back</AppButton>
    </div>

    <form class="space-y-6" @submit.prevent="handleSubmit">
      <!-- Header fields -->
      <div class="card p-5 grid grid-cols-2 gap-4">
        <div class="col-span-2">
          <label class="label">Supplier <span class="text-red-500">*</span></label>
          <select v-model="form.supplier" class="input">
            <option value="">Select supplier…</option>
            <option v-for="s in suppliers" :key="s.id" :value="s.id">{{ s.name }}</option>
          </select>
        </div>
        <AppInput v-model="form.expected_delivery" label="Expected Delivery" type="date" />
        <AppInput v-model="form.notes" label="Notes" placeholder="Optional" />
      </div>

      <!-- Line items -->
      <div class="card overflow-hidden">
        <div class="px-4 py-3 border-b border-gray-100 font-semibold text-sm">Items</div>
        <table class="table-base">
          <thead><tr><th>Product</th><th class="text-right">Qty</th><th class="text-right">Unit Cost</th><th class="text-right">Total</th><th></th></tr></thead>
          <tbody>
            <tr v-for="(line, i) in form.lines" :key="i">
              <td class="px-3 py-2">{{ line.product_name }}</td>
              <td class="px-3 py-2 text-right">{{ line.qty }}</td>
              <td class="px-3 py-2 text-right"><MoneyDisplay :value="line.unit_cost" /></td>
              <td class="px-3 py-2 text-right font-medium"><MoneyDisplay :value="line.qty * line.unit_cost" /></td>
              <td class="px-3 py-2 text-right">
                <button type="button" class="text-xs text-red-500 hover:text-red-700" @click="removeLine(i)">Remove</button>
              </td>
            </tr>
            <!-- Add line row -->
            <tr class="bg-blue-50/50">
              <td class="px-3 py-2">
                <select v-model="newLine.product" class="input text-sm">
                  <option value="">Select product…</option>
                  <option v-for="p in products" :key="p.id" :value="p.id">{{ p.name }}</option>
                </select>
              </td>
              <td class="px-3 py-2"><input v-model.number="newLine.qty" type="number" min="1" class="input text-sm text-right" /></td>
              <td class="px-3 py-2"><input v-model.number="newLine.unit_cost" type="number" min="0" class="input text-sm text-right" /></td>
              <td class="px-3 py-2 text-right font-medium money text-sm">{{ formatMoney(newLine.qty * newLine.unit_cost) }}</td>
              <td class="px-3 py-2 text-right">
                <AppButton type="button" variant="secondary" size="sm" @click="addLine">+ Add</AppButton>
              </td>
            </tr>
          </tbody>
          <tfoot>
            <tr class="bg-gray-50">
              <td colspan="3" class="px-3 py-2.5 text-right text-sm font-semibold text-gray-600">Order Total</td>
              <td class="px-3 py-2.5 text-right font-bold text-gray-900"><MoneyDisplay :value="total" /></td>
              <td></td>
            </tr>
          </tfoot>
        </table>
      </div>

      <div class="flex justify-end gap-3">
        <AppButton type="button" variant="secondary" @click="router.back()">Cancel</AppButton>
        <AppButton type="submit" variant="primary" :loading="saving">Create Order</AppButton>
      </div>
    </form>
  </div>
</template>
