<script setup>
import { ref, onMounted } from 'vue'
import { settingsApi } from '@/api/settings'
import { useUiStore } from '@/stores/ui'
import { PERMISSIONS } from '@/utils/constants'
import AppButton from '@/components/ui/AppButton.vue'

const ui    = useUiStore()
const roles = ref([])
const loading = ref(true)
const saving  = ref(null)

const PERMISSION_LABELS = {
  [PERMISSIONS.VIEW_COST]:           'View Cost Prices',
  [PERMISSIONS.VIEW_PROFIT]:         'View Profit / P&L',
  [PERMISSIONS.VIEW_REPORTS]:        'View Reports',
  [PERMISSIONS.MANAGE_USERS]:        'Manage Users',
  [PERMISSIONS.VOID_INVOICES]:       'Void Invoices',
  [PERMISSIONS.MANAGE_DISCOUNTS]:    'Manage Discounts',
  [PERMISSIONS.MANAGE_PURCHASE]:     'Manage Purchases',
  [PERMISSIONS.MANAGE_REPAIRS]:      'Manage Repairs',
  [PERMISSIONS.MANAGE_INSTALLMENTS]: 'Manage Installments',
}

onMounted(async () => {
  const res = await settingsApi.listRoles()
  roles.value  = res.data.results ?? res.data
  loading.value = false
})

function toggle(role, perm) {
  const perms = role.permissions
  const idx   = perms.indexOf(perm)
  if (idx >= 0) perms.splice(idx, 1)
  else perms.push(perm)
}

async function saveRole(role) {
  saving.value = role.id
  try {
    await settingsApi.updateRole(role.id, { permissions: role.permissions })
    ui.toastSuccess(`Role "${role.name}" updated`)
  } catch (e) {
    ui.toastError(e.displayMessage || 'Save failed')
  } finally { saving.value = null }
}
</script>

<template>
  <div class="space-y-6">
    <div
      v-for="role in roles"
      :key="role.id"
      class="card p-5"
    >
      <div class="flex items-center justify-between mb-4">
        <div>
          <h3 class="font-semibold text-gray-900">{{ role.name }}</h3>
          <p class="text-xs text-gray-500">{{ role.description }}</p>
        </div>
        <AppButton variant="primary" size="sm" :loading="saving === role.id" @click="saveRole(role)">Save</AppButton>
      </div>
      <div class="grid grid-cols-2 md:grid-cols-3 gap-3">
        <label
          v-for="(label, perm) in PERMISSION_LABELS"
          :key="perm"
          class="flex items-center gap-2 text-sm cursor-pointer"
        >
          <input
            type="checkbox"
            :checked="role.permissions.includes(perm)"
            class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            @change="toggle(role, perm)"
          />
          {{ label }}
        </label>
      </div>
    </div>
    <p v-if="!loading && roles.length === 0" class="text-sm text-gray-400">No roles configured</p>
  </div>
</template>
