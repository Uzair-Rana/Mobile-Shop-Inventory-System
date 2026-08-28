<script setup>
import { computed } from 'vue'
import { useRoute, RouterView } from 'vue-router'
import AppShell from '@/components/layout/AppShell.vue'
import ToastContainer from '@/components/ui/ToastContainer.vue'
import ConfirmDialog from '@/components/ui/ConfirmDialog.vue'
import { useAuthStore } from '@/stores/auth'

const auth  = useAuthStore()
const route = useRoute()

// Routes marked fullscreen (POS) bypass the AppShell entirely
const isFullscreen  = computed(() => route.meta?.fullscreen === true)
const isPublicRoute = computed(() => route.meta?.public === true)
const showShell     = computed(() => auth.isLoggedIn && !isFullscreen.value && !isPublicRoute.value)
</script>

<template>
  <!-- Global overlays — always rendered so they can appear on any screen -->
  <ToastContainer />
  <ConfirmDialog />

  <!-- Authenticated + standard layout -->
  <AppShell v-if="showShell">
    <RouterView />
  </AppShell>

  <!-- Fullscreen (POS) or public (login) routes -->
  <RouterView v-else />
</template>
