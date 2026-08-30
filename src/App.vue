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
  <!-- Global overlays — always rendered so they can appear on any screen -->
  <ToastContainer />
  <ConfirmDialog />

  <!-- Standard layout with sidebar/topbar -->
  <AppShell v-if="!isFullscreen">
    <RouterView />
  </AppShell>

  <!-- Fullscreen routes (POS) -->
  <RouterView v-else />
</template>
