<script setup>
/**
 * PermGate — renders slot only if current user has the given permission.
 * Silent if permission is missing (no placeholder, no error).
 */
import { computed } from 'vue'
import { usePermissions } from '@/composables/usePermissions'

const props = defineProps({
  perm: { type: String, required: true },
})

const perms = usePermissions()
const allowed = computed(() => perms.can(props.perm))
</script>

<template>
  <slot v-if="allowed" />
</template>
