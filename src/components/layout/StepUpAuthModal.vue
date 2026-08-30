<script setup>
/**
 * StepUpAuthModal — password re-confirmation modal for sensitive actions.
 * Driven by ui store's stepUpAuthDialog state.
 */
import { ref } from 'vue'
import { useUiStore } from '@/stores/ui'
import { useAuthStore } from '@/stores/auth'
import { userFixtures } from '@/api/mock/db/fixtures/users'
import AppModal from '@/components/ui/AppModal.vue'
import AppButton from '@/components/ui/AppButton.vue'

const ui = useUiStore()
const auth = useAuthStore()

const password = ref('')
const error = ref('')
const checking = ref(false)

async function handleConfirm() {
  if (!password.value) { error.value = 'Password required'; return }
  checking.value = true
  error.value = ''
  await new Promise(r => setTimeout(r, 150))

  const user = userFixtures.find(u => u.id === auth.user?.id)
  if (user && user.password === password.value) {
    password.value = ''
    checking.value = false
    ui.resolveStepUp(true)
  } else {
    error.value = 'Incorrect password'
    checking.value = false
  }
}

function handleCancel() {
  password.value = ''
  error.value = ''
  ui.resolveStepUp(false)
}
</script>

<template>
  <AppModal
    :open="ui.stepUpAuthDialog.open"
    title="Confirm Your Identity"
    size="sm"
    @close="handleCancel"
  >
    <div class="space-y-3">
      <div class="flex items-start gap-2.5 rounded bg-amber-50 border border-amber-200 px-3 py-2.5">
        <svg class="w-3.5 h-3.5 text-amber-600 mt-0.5 shrink-0" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 15v2m0 0h.01M12 10a3 3 0 00-3 3 3 3 0 003 3 3 3 0 003-3 3 3 0 00-3-3zm0-7a9 9 0 100 18A9 9 0 0012 3z"/>
        </svg>
        <div>
          <p class="text-[11px] font-bold text-amber-800 uppercase tracking-wide mb-0.5">Step-Up Required</p>
          <p class="text-xs text-amber-700">{{ ui.stepUpAuthDialog.action }}</p>
        </div>
      </div>

      <div>
        <label class="label">Enter your password to continue</label>
        <input
          v-model="password"
          type="password"
          class="input"
          placeholder="Your password"
          autocomplete="current-password"
          @keydown.enter="handleConfirm"
        />
      </div>

      <p v-if="error" class="text-xs text-red-600">{{ error }}</p>
    </div>

    <template #footer>
      <AppButton variant="secondary" @click="handleCancel">Cancel</AppButton>
      <AppButton variant="primary" :loading="checking" @click="handleConfirm">Verify</AppButton>
    </template>
  </AppModal>
</template>
