<script setup>
import { ref, onMounted } from 'vue'
import { settingsApi } from '@/api/settings'
import { useUiStore } from '@/stores/ui'
import { useConfirm } from '@/composables/useConfirm'
import AppTable from '@/components/ui/AppTable.vue'
import AppButton from '@/components/ui/AppButton.vue'
import AppBadge from '@/components/ui/AppBadge.vue'
import { formatDate } from '@/utils/date'

const ui    = useUiStore()
const { confirm } = useConfirm()
const users  = ref([])
const loading= ref(true)

const columns = [
  { key: 'name',     label: 'Name' },
  { key: 'username', label: 'Username' },
  { key: 'role',     label: 'Role' },
  { key: 'status',   label: 'Status' },
  { key: 'last',     label: 'Last Login' },
  { key: 'actions',  label: '' },
]

onMounted(async () => {
  const res = await settingsApi.listUsers()
  users.value  = res.data.results ?? res.data
  loading.value = false
})

async function deactivate(user) {
  const ok = await confirm({
    title:  `Deactivate ${user.username}`,
    message: 'This user will no longer be able to log in.',
    effect: 'No data will be deleted. Their historical records are preserved.',
    confirmLabel: 'Deactivate User',
    confirmClass: 'btn-danger',
  })
  if (!ok) return
  try {
    await settingsApi.deactivateUser(user.id)
    ui.toastSuccess('User deactivated')
    const res = await settingsApi.listUsers()
    users.value = res.data.results ?? res.data
  } catch (e) {
    ui.toastError(e.displayMessage || 'Failed')
  }
}
</script>

<template>
  <div class="space-y-4">
    <div class="flex justify-end">
      <AppButton variant="primary">+ Add User</AppButton>
    </div>

    <AppTable :columns="columns" :loading="loading" empty-message="No users found">
      <tr v-for="u in users" :key="u.id">
        <td class="px-3 py-2.5">{{ u.first_name }} {{ u.last_name }}</td>
        <td class="px-3 py-2.5 text-sm font-mono text-gray-600">{{ u.username }}</td>
        <td class="px-3 py-2.5 text-sm">{{ u.role_display || 'Staff' }}</td>
        <td class="px-3 py-2.5">
          <AppBadge
            :label="u.is_active ? 'Active' : 'Inactive'"
            :variant="u.is_active ? 'badge-green' : 'badge-gray'"
          />
        </td>
        <td class="px-3 py-2.5 text-sm text-gray-500">{{ formatDate(u.last_login) || 'Never' }}</td>
        <td class="px-3 py-2.5 text-right">
          <button v-if="u.is_active" class="text-xs text-red-500 hover:text-red-700" @click="deactivate(u)">Deactivate</button>
        </td>
      </tr>
    </AppTable>
  </div>
</template>
