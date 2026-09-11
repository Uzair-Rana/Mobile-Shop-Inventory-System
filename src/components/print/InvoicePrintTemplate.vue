<script setup>
import { computed } from 'vue'
import { formatDate, formatDateTime } from '@/utils/date'
import { formatMoney } from '@/utils/money'
import MoneyDisplay from '@/components/ui/MoneyDisplay.vue'

const props = defineProps({
  invoice: {
    type: Object,
    required: true,
  },
  companyName: {
    type: String,
    default: 'Mobile Shop',
  },
  companyPhone: {
    type: String,
    default: '',
  },
})

const statusBadgeClass = computed(() => {
  const statusMap = {
    paid: 'badge-paid',
    finalized: 'badge-finalized',
    draft: 'badge-draft',
    voided: 'badge-voided',
    returned: 'badge-returned',
    partially_paid: 'badge-partially_paid',
  }
  return statusMap[props.invoice.status] || 'badge-gray'
})

const totalItems = computed(() => {
  return (props.invoice.lines || []).reduce((sum, line) => sum + line.qty, 0)
})
</script>

<template>
  <div id="invoice-print-template" style="display: none;">
    <div style="padding: 40px; max-width: 900px;">
      <!-- Header -->
      <div style="margin-bottom: 40px; border-bottom: 2px solid #1f2937; padding-bottom: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px;">
          <div>
            <h1 style="font-size: 24px; font-weight: bold; margin-bottom: 5px; color: #1f2937;">
              {{ companyName }}
            </h1>
            <p v-if="companyPhone" style="font-size: 13px; color: #6b7280; margin: 0;">
              Phone: {{ companyPhone }}
            </p>
          </div>
          <div style="text-align: right;">
            <p style="font-size: 28px; font-weight: bold; color: #1f2937; margin: 0;">INVOICE</p>
            <p style="font-size: 16px; color: #6b7280; margin: 5px 0 0 0;">
              #{{ invoice.invoice_number }}
            </p>
          </div>
        </div>

        <!-- Invoice Info -->
        <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; font-size: 13px; color: #6b7280; margin-top: 20px;">
          <div>
            <p style="font-weight: 600; color: #1f2937; margin-bottom: 5px;">Invoice Date</p>
            <p style="margin: 0;">{{ formatDate(invoice.created_at) }}</p>
          </div>
          <div>
            <p style="font-weight: 600; color: #1f2937; margin-bottom: 5px;">Customer</p>
            <p style="margin: 0;">{{ invoice.customer_name || 'Walk-in Customer' }}</p>
          </div>
          <div>
            <p style="font-weight: 600; color: #1f2937; margin-bottom: 5px;">Status</p>
            <p style="margin: 0;">
              <span :class="`badge ${statusBadgeClass}`" style="display: inline-block; padding: 4px 8px; border-radius: 4px; font-weight: 600; font-size: 12px;">
                {{ invoice.status.toUpperCase() }}
              </span>
            </p>
          </div>
        </div>
      </div>

      <!-- Line Items -->
      <div style="margin-bottom: 30px;">
        <table style="width: 100%; border-collapse: collapse;">
          <thead>
            <tr style="background-color: #f3f4f6; border-bottom: 2px solid #1f2937;">
              <th style="padding: 12px; text-align: left; font-weight: 600; font-size: 13px;">Product</th>
              <th style="padding: 12px; text-align: left; font-weight: 600; font-size: 13px;">IMEI</th>
              <th style="padding: 12px; text-align: right; font-weight: 600; font-size: 13px;">Qty</th>
              <th style="padding: 12px; text-align: right; font-weight: 600; font-size: 13px;">Unit Price</th>
              <th style="padding: 12px; text-align: right; font-weight: 600; font-size: 13px;">Discount</th>
              <th style="padding: 12px; text-align: right; font-weight: 600; font-size: 13px;">Total</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="line in invoice.lines" :key="line.id" style="border-bottom: 1px solid #e5e7eb;">
              <td style="padding: 12px; font-size: 14px;">{{ line.product_name }}</td>
              <td style="padding: 12px; font-size: 12px; font-family: monospace; color: #6b7280;">{{ line.imei || '—' }}</td>
              <td style="padding: 12px; text-align: right; font-size: 14px;">{{ line.qty }}</td>
              <td style="padding: 12px; text-align: right; font-size: 14px;">{{ formatMoney(line.unit_price) }}</td>
              <td style="padding: 12px; text-align: right; font-size: 14px; color: #059669;">
                <span v-if="line.discount_abs > 0">{{ formatMoney(line.discount_abs) }}</span>
                <span v-else-if="line.discount_pct > 0">{{ line.discount_pct }}%</span>
                <span v-else style="color: #9ca3af;">—</span>
              </td>
              <td style="padding: 12px; text-align: right; font-size: 14px; font-weight: 500;">{{ formatMoney(line.line_total) }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Totals Section -->
      <div style="display: flex; justify-content: flex-end; margin-bottom: 40px;">
        <table style="width: 300px; border-collapse: collapse;">
          <tbody>
            <tr style="border-bottom: 1px solid #e5e7eb;">
              <td style="padding: 8px 12px; text-align: left; color: #6b7280; font-size: 13px;">Subtotal</td>
              <td style="padding: 8px 12px; text-align: right; font-size: 14px; font-weight: 500;">{{ formatMoney(invoice.subtotal) }}</td>
            </tr>
            <tr v-if="invoice.tax_amount > 0" style="border-bottom: 1px solid #e5e7eb;">
              <td style="padding: 8px 12px; text-align: left; color: #6b7280; font-size: 13px;">Tax</td>
              <td style="padding: 8px 12px; text-align: right; font-size: 14px; font-weight: 500;">{{ formatMoney(invoice.tax_amount) }}</td>
            </tr>
            <tr v-if="invoice.invoice_discount > 0" style="border-bottom: 1px solid #e5e7eb;">
              <td style="padding: 8px 12px; text-align: left; color: #059669; font-size: 13px;">Discount</td>
              <td style="padding: 8px 12px; text-align: right; font-size: 14px; font-weight: 500; color: #059669;">−{{ formatMoney(invoice.invoice_discount) }}</td>
            </tr>
            <tr style="border-top: 2px solid #1f2937; border-bottom: 2px solid #1f2937; font-weight: 600; font-size: 16px;">
              <td style="padding: 12px; text-align: left;">Grand Total</td>
              <td style="padding: 12px; text-align: right;">{{ formatMoney(invoice.grand_total) }}</td>
            </tr>
            <tr style="border-bottom: 1px solid #e5e7eb;">
              <td style="padding: 8px 12px; text-align: left; color: #6b7280; font-size: 13px;">Amount Paid</td>
              <td style="padding: 8px 12px; text-align: right; font-size: 14px; font-weight: 500;">{{ formatMoney(invoice.amount_paid) }}</td>
            </tr>
            <tr v-if="invoice.balance_due > 0">
              <td style="padding: 8px 12px; text-align: left; color: #dc2626; font-size: 13px; font-weight: 600;">Balance Due</td>
              <td style="padding: 8px 12px; text-align: right; font-size: 14px; font-weight: 600; color: #dc2626;">{{ formatMoney(invoice.balance_due) }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Footer -->
      <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #e5e7eb; font-size: 12px; color: #6b7280; text-align: center;">
        <p style="margin: 0; margin-bottom: 8px;">Thank you for your business!</p>
        <p style="margin: 0; font-size: 11px;">
          Invoice printed on {{ formatDateTime(new Date().toISOString()) }}
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
}

.badge-paid {
  background-color: #dcfce7;
  color: #166534;
}

.badge-finalized {
  background-color: #dbeafe;
  color: #0c4a6e;
}

.badge-draft {
  background-color: #fef3c7;
  color: #92400e;
}

.badge-voided {
  background-color: #fee2e2;
  color: #991b1b;
}

.badge-returned {
  background-color: #fce7f3;
  color: #831843;
}

.badge-partially_paid {
  background-color: #f3e8ff;
  color: #6b21a8;
}
</style>
