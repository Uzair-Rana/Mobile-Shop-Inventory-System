<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, RouterView } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import AppShell from '@/components/layout/AppShell.vue'
import ToastContainer from '@/components/ui/ToastContainer.vue'
import ConfirmDialog from '@/components/ui/ConfirmDialog.vue'
import SplashScreen from '@/components/SplashScreen.vue'

const route = useRoute()
const auth  = useAuthStore()

// POS is fullscreen — no sidebar/topbar
const isFullscreen = computed(() => route.meta?.fullscreen === true)

// ── Splash logic ──────────────────────────────────────────────────────────────
// Show splash ONCE per app load.
// Skip entirely if user already has a valid token (they're already logged in —
// splash should never block re-entry mid-session).
const showSplash = ref(!auth.isLoggedIn)

function onSplashDone() {
  showSplash.value = false
}

// Safety: if the token check resolves quickly and user IS logged in,
// dismiss the splash immediately (shouldn't normally show anyway).
onMounted(() => {
  if (auth.isLoggedIn) showSplash.value = false
})
</script>

<template>
  <!-- Splash — rendered once, removed from DOM after done -->
  <SplashScreen v-if="showSplash" @done="onSplashDone" />

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
