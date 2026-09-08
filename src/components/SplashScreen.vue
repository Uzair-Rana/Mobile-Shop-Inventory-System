<script setup>
/**
 * SplashScreen — shown once per app load.
 * Emits 'done' when the exit animation finishes.
 * Parent must v-if on this component (remove it from DOM after done).
 */
import { ref, onMounted } from 'vue'
import logoImg from '@/assets/logo of My Phone.png'

const emit = defineEmits(['done'])

// Three phases:
//  'enter'  — logo fades + scales in (0 → 1)
//  'hold'   — brief pause at full opacity
//  'exit'   — logo zooms out + fades (scale up, opacity → 0)
const phase = ref('enter')

onMounted(() => {
  // enter: 600ms, hold: 800ms, exit: 500ms
  setTimeout(() => { phase.value = 'hold'  },  600)
  setTimeout(() => { phase.value = 'exit'  }, 1400)
  setTimeout(() => { emit('done')           }, 1950)
})
</script>

<template>
  <Teleport to="body">
    <div class="splash-overlay" :class="`splash-${phase}`">
      <!-- Dark radial background that matches sidebar -->
      <div class="splash-bg" />

      <!-- Decorative blobs -->
      <div class="blob b1" />
      <div class="blob b2" />

      <!-- Logo + wordmark -->
      <div class="splash-content" :class="`content-${phase}`">
        <img :src="logoImg" alt="My Phone" class="splash-logo" />
        <p class="splash-name">My Phone</p>
        <p class="splash-tagline">Mobile Shop ERP</p>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
/* ── Overlay ──────────────────────────────────────────────────────────────── */
.splash-overlay {
  position: fixed;
  inset: 0;
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  /* overlay itself fades out at the very end */
  transition: opacity 200ms ease 1750ms;
  opacity: 1;
}
/* keep visible during enter + hold, fade at exit end */
.splash-exit { opacity: 0; transition: opacity 200ms ease 1700ms; }

/* ── Background ───────────────────────────────────────────────────────────── */
.splash-bg {
  position: absolute;
  inset: 0;
  background: #0d0f14;
  background-image:
    radial-gradient(ellipse at 50% 40%, rgba(225,29,72,.18) 0%, transparent 55%),
    radial-gradient(ellipse at 80% 80%, rgba(29,78,216,.10) 0%, transparent 50%);
}

/* ── Blobs ────────────────────────────────────────────────────────────────── */
.blob {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  pointer-events: none;
}
.b1 { width:500px; height:500px; background:rgba(225,29,72,.10); top:-100px; left:-100px; }
.b2 { width:300px; height:300px; background:rgba(29,78,216,.07);  bottom:-80px; right:-80px; }

/* ── Content ──────────────────────────────────────────────────────────────── */
.splash-content {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.875rem;
  /* default: invisible before enter */
  opacity: 0;
  transform: scale(0.72);
  transition: opacity 600ms cubic-bezier(0.34, 1.56, 0.64, 1),
              transform 600ms cubic-bezier(0.34, 1.56, 0.64, 1);
}

/* ENTER → scale up + fade in */
.content-enter,
.content-hold {
  opacity: 1;
  transform: scale(1);
}

/* EXIT → zoom out + fade */
.content-exit {
  opacity: 0;
  transform: scale(1.35);
  transition: opacity 500ms ease,
              transform 500ms cubic-bezier(0.4, 0, 0.6, 1);
}

/* ── Logo image ───────────────────────────────────────────────────────────── */
.splash-logo {
  width: 108px;
  height: 108px;
  object-fit: contain;
  border-radius: 26px;
  background: rgba(255,255,255,.05);
  padding: 8px;
  box-shadow:
    0 0 0 1px rgba(255,255,255,.08),
    0 8px 40px rgba(225,29,72,.35),
    0 4px 16px rgba(0,0,0,.4);
}

/* ── Wordmark ─────────────────────────────────────────────────────────────── */
.splash-name {
  font-family: 'Inter', system-ui, sans-serif;
  font-size: 2rem;
  font-weight: 900;
  color: #ffffff;
  letter-spacing: -0.04em;
  line-height: 1;
  margin: 0;
}

.splash-tagline {
  font-family: 'Inter', system-ui, sans-serif;
  font-size: 0.8rem;
  font-weight: 600;
  color: #fb7185;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  margin: 0;
}
</style>
