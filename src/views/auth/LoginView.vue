<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import logoImg from '@/assets/logo of My Phone.png'

const router = useRouter()
const auth   = useAuthStore()

const username  = ref('')
const password  = ref('')
const showPass  = ref(false)
const loading   = ref(false)
const errorMsg  = ref('')

// Redirect if already logged in
onMounted(() => {
  if (auth.isLoggedIn) router.push('/dashboard')
})

async function handleLogin() {
  if (!username.value || !password.value) {
    errorMsg.value = 'Please enter username and password.'
    return
  }
  loading.value = true
  errorMsg.value = ''
  try {
    await auth.login({ username: username.value, password: password.value })
    router.push('/dashboard')
  } catch (e) {
    errorMsg.value = e.displayMessage || 'Invalid credentials. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-bg">
    <!-- Decorative blobs -->
    <div class="blob blob-1" />
    <div class="blob blob-2" />
    <div class="blob blob-3" />

    <div class="login-card">
      <!-- Logo -->
      <div class="logo-wrap">
        <img :src="logoImg" alt="My Phone" class="logo-img" />
      </div>

      <!-- Heading -->
      <div class="text-center mb-6">
        <h1 class="login-title">My Phone</h1>
        <p class="login-sub">Mobile Shop Management System</p>
      </div>

      <!-- Form -->
      <form class="space-y-4" @submit.prevent="handleLogin">
        <!-- Username -->
        <div>
          <label class="label">Username</label>
          <div class="input-icon-wrap">
            <svg class="input-icon" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
            </svg>
            <input
              v-model="username"
              type="text"
              class="input input-icon-left"
              placeholder="Enter your username"
              autocomplete="username"
              autofocus
            />
          </div>
        </div>

        <!-- Password -->
        <div>
          <label class="label">Password</label>
          <div class="input-icon-wrap">
            <svg class="input-icon" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
            </svg>
            <input
              v-model="password"
              :type="showPass ? 'text' : 'password'"
              class="input input-icon-left input-icon-right"
              placeholder="Enter your password"
              autocomplete="current-password"
            />
            <button
              type="button"
              class="input-icon-btn"
              tabindex="-1"
              @click="showPass = !showPass"
            >
              <svg v-if="!showPass" class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                <path stroke-linecap="round" stroke-linejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
              </svg>
              <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"/>
              </svg>
            </button>
          </div>
        </div>

        <!-- Error -->
        <Transition name="fade">
          <div v-if="errorMsg" class="error-alert">
            <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
            {{ errorMsg }}
          </div>
        </Transition>

        <!-- Submit -->
        <button
          type="submit"
          class="btn btn-primary w-full btn-lg mt-2"
          :disabled="loading"
        >
          <svg v-if="loading" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
          </svg>
          <span>{{ loading ? 'Signing in…' : 'Sign In' }}</span>
        </button>
      </form>

      <!-- Footer hint -->
      <p class="login-footer">
        My Phone ERP &copy; {{ new Date().getFullYear() }}
      </p>
    </div>
  </div>
</template>

<style scoped>
.login-bg {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #0d0f14;
  background-image:
    radial-gradient(ellipse at 30% 20%, rgba(225,29,72,.15) 0%, transparent 50%),
    radial-gradient(ellipse at 70% 80%, rgba(29,78,216,.10) 0%, transparent 50%);
  padding: 1.5rem;
  position: relative;
  overflow: hidden;
}

/* Decorative blobs */
.blob {
  position: absolute;
  border-radius: 50%;
  filter: blur(60px);
  pointer-events: none;
  z-index: 0;
}
.blob-1 { width: 400px; height: 400px; background: rgba(225,29,72,.12); top: -100px; left: -100px; }
.blob-2 { width: 300px; height: 300px; background: rgba(29,78,216,.08);  bottom: -80px; right: -80px; }
.blob-3 { width: 200px; height: 200px; background: rgba(251,113,133,.08); top: 50%; left: 50%; transform: translate(-50%,-50%); }

.login-card {
  width: 100%;
  max-width: 400px;
  background: rgba(255,255,255,.97);
  border-radius: 20px;
  padding: 2.25rem 2rem 1.75rem;
  box-shadow:
    0 0 0 1px rgba(255,255,255,.1),
    0 25px 60px rgba(0,0,0,.5),
    0 4px 16px rgba(225,29,72,.15);
  position: relative;
  z-index: 1;
}

/* Logo */
.logo-wrap {
  display: flex;
  justify-content: center;
  margin-bottom: 1.25rem;
}
.logo-img {
  width: 80px;
  height: 80px;
  object-fit: contain;
  border-radius: 18px;
  background: #f9fafb;
  padding: 6px;
  box-shadow: 0 4px 20px rgba(225,29,72,.25), 0 2px 8px rgba(0,0,0,.1);
}

.login-title {
  font-size: 1.625rem;
  font-weight: 900;
  color: #0d0f14;
  letter-spacing: -0.03em;
}
.login-sub {
  font-size: 0.8rem;
  color: #6b7280;
  margin-top: 0.2rem;
}

/* Input with icon */
.input-icon-wrap { position: relative; }
.input-icon {
  position: absolute;
  left: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  width: 16px; height: 16px;
  color: #9ca3af;
  pointer-events: none;
}
.input-icon-left  { padding-left: 2.25rem; }
.input-icon-right { padding-right: 2.5rem; }
.input-icon-btn {
  position: absolute;
  right: 0.625rem;
  top: 50%;
  transform: translateY(-50%);
  color: #9ca3af;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 4px;
  transition: color 120ms;
}
.input-icon-btn:hover { color: #4b5563; }

/* Error */
.error-alert {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: #fff1f2;
  border: 1px solid #fecdd3;
  border-radius: 8px;
  padding: 0.625rem 0.875rem;
  font-size: 0.8rem;
  color: #be123c;
  font-weight: 500;
}

.login-footer {
  text-align: center;
  font-size: 0.7rem;
  color: #9ca3af;
  margin-top: 1.5rem;
}

/* Transition */
.fade-enter-active, .fade-leave-active { transition: all 200ms ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; transform: translateY(-4px); }

@keyframes spin { to { transform: rotate(360deg); } }
.animate-spin { animation: spin .7s linear infinite; }
</style>
