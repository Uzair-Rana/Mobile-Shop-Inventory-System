<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import AppSidebar from './AppSidebar.vue'
import AppTopBar from './AppTopBar.vue'

const route     = useRoute()
const pageTitle = computed(() => route.meta?.title || 'Dashboard')
</script>

<template>
  <div class="shell">
    <AppSidebar />
    <div class="shell-main">
      <AppTopBar :title="pageTitle" />
      <main class="shell-content">
        <div class="shell-inner">
          <slot />
        </div>
      </main>
    </div>
  </div>
</template>

<style scoped>
.shell {
  display: flex;
  height: 100vh;
  overflow: hidden;
  background: #f0f4f8;
}

.shell-main {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.shell-content {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
}

.shell-inner {
  padding: 1.25rem 1.5rem;
  max-width: 1600px;
  animation: page-in 200ms ease-out;
}

@keyframes page-in {
  from { opacity: 0; transform: translateY(6px); }
  to   { opacity: 1; transform: translateY(0); }
}
</style>
