<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import AppSidebar from './AppSidebar.vue'
import AppTopBar from './AppTopBar.vue'

const route     = useRoute()
const pageTitle = computed(() => route.meta?.title || 'DEVNEST')
</script>

<template>
  <div class="flex h-screen overflow-hidden" style="background:#f0f1f3">
    <AppSidebar />
    <div class="flex-1 flex flex-col min-w-0 overflow-hidden">
      <AppTopBar :title="pageTitle" />
      <!--
        Tight padding: 12px all sides on desktop.
        Content is dense data — no hero whitespace needed.
      -->
      <main class="flex-1 overflow-y-auto p-3">
        <slot />
      </main>
    </div>
  </div>
</template>
