<script setup>
import { computed } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import { SECTIONS } from '@/config/sections'
import NavIcon from '@/components/ui/NavIcon.vue'

const route = useRoute()
const section = computed(() =>
  SECTIONS.find(s => s.key === route.meta.sectionKey) ||
  SECTIONS.find(s => route.path.startsWith(s.to))
)
</script>

<template>
  <div v-if="section" class="space-y-6">
    <div class="page-header">
      <div>
        <h1 class="page-title gradient-text">{{ section.label }}</h1>
        <p class="page-subtitle">{{ section.description }}</p>
      </div>
    </div>

    <div class="hub-grid">
      <RouterLink
        v-for="(it, i) in section.items"
        :key="it.to"
        :to="it.to"
        class="hub-card card"
        :style="{ '--i': i }"
      >
        <span class="hub-icon">
          <NavIcon :icon="it.icon" class="w-6 h-6" />
        </span>
        <div class="min-w-0">
          <p class="hub-title">{{ it.label }}</p>
          <p class="hub-desc">{{ it.desc }}</p>
        </div>
        <span class="hub-arrow">→</span>
      </RouterLink>
    </div>
  </div>
</template>

<style scoped>
.hub-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 1rem;
}

.hub-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.25rem 1.35rem;
  text-decoration: none;
  position: relative;
  overflow: hidden;
}

/* Rotating accent color per card (bold & colorful) */
.hub-icon {
  width: 48px; height: 48px;
  flex-shrink: 0;
  border-radius: 14px;
  display: flex; align-items: center; justify-content: center;
  color: #fff;
  background: linear-gradient(135deg, var(--c-rose-1), var(--c-rose-2));
  box-shadow: var(--glow-brand);
}
.hub-card:nth-child(6n+2) .hub-icon { background: linear-gradient(135deg, var(--c-blue-1),    var(--c-blue-2));    box-shadow: var(--glow-blue); }
.hub-card:nth-child(6n+3) .hub-icon { background: linear-gradient(135deg, var(--c-emerald-1), var(--c-emerald-2)); box-shadow: var(--glow-emerald); }
.hub-card:nth-child(6n+4) .hub-icon { background: linear-gradient(135deg, var(--c-amber-1),   var(--c-amber-2));   box-shadow: var(--glow-amber); }
.hub-card:nth-child(6n+5) .hub-icon { background: linear-gradient(135deg, var(--c-violet-1),  var(--c-violet-2));  box-shadow: var(--glow-violet); }
.hub-card:nth-child(6n+6) .hub-icon { background: linear-gradient(135deg, var(--c-cyan-1),    var(--c-cyan-2));    box-shadow: var(--glow-blue); }

.hub-title {
  font-size: 1rem;
  font-weight: 800;
  color: var(--text-primary);
  letter-spacing: -.01em;
}
.hub-desc {
  font-size: .8125rem;
  color: var(--text-muted);
  margin-top: .15rem;
}
.hub-arrow {
  margin-left: auto;
  font-size: 1.1rem;
  font-weight: 800;
  color: var(--text-muted);
  transition: transform 180ms, color 180ms;
}
.hub-card:hover .hub-arrow {
  transform: translateX(4px);
  color: var(--brand-500);
}
</style>
