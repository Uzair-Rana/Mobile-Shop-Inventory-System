<script setup>
/**
 * ConfirmDialog — global. Always shows the financial/inventory `effect`
 * for destructive actions. Compact layout, no wasted vertical space.
 */
import { useUiStore } from '@/stores/ui'
import AppModal from './AppModal.vue'
import AppButton from './AppButton.vue'

const ui = useUiStore()
</script>

<template>
  <AppModal
    :open="ui.confirmDialog.open"
    :title="ui.confirmDialog.title"
    size="sm"
    @close="ui.resolveConfirm(false)"
  >
    <div class="space-y-3">
      <p class="text-sm text-gray-700 leading-snug">{{ ui.confirmDialog.message }}</p>

      <!--
        Effect panel — required for all destructive/reversal actions.
        States exactly what will happen to inventory and finances BEFORE the user clicks.
      -->
      <div
        v-if="ui.confirmDialog.effect"
        class="flex gap-2.5 rounded bg-amber-50 border border-amber-200 px-3 py-2.5"
        role="note"
      >
        <svg class="w-3.5 h-3.5 text-amber-600 mt-0.5 shrink-0" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" aria-hidden="true">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v4m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/>
        </svg>
        <div>
          <p class="text-[11px] font-bold text-amber-800 uppercase tracking-wide mb-0.5">What this will do</p>
          <p class="text-xs text-amber-700 leading-snug">{{ ui.confirmDialog.effect }}</p>
        </div>
      </div>
    </div>

    <template #footer>
      <AppButton variant="secondary" @click="ui.resolveConfirm(false)">Cancel</AppButton>
      <AppButton
        :variant="ui.confirmDialog.confirmClass === 'btn-danger' ? 'danger' : 'primary'"
        @click="ui.resolveConfirm(true)"
      >
        {{ ui.confirmDialog.confirmLabel }}
      </AppButton>
    </template>
  </AppModal>
</template>
