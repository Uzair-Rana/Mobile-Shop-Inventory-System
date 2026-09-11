<script setup>
import { computed } from 'vue'
import { useRoute, RouterView } from 'vue-router'
import AppShell from '@/components/layout/AppShell.vue'
import ToastContainer from '@/components/ui/ToastContainer.vue'
import ConfirmDialog from '@/components/ui/ConfirmDialog.vue'

const route = useRoute()

// POS is fullscreen — no sidebar/topbar
const isFullscreen = computed(() => route.meta?.fullscreen === true)
</script>

<template>
  <ToastContainer />
  <ConfirmDialog />

  <AppShell v-if="!isFullscreen">
    <RouterView />
  </AppShell>

  <RouterView v-else />
</template>
