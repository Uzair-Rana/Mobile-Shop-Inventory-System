<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import AppInput from '@/components/ui/AppInput.vue'
import AppButton from '@/components/ui/AppButton.vue'

const auth   = useAuthStore()
const router = useRouter()
const route  = useRoute()

const username = ref('')
const password = ref('')
const error    = ref('')

async function handleLogin() {
  error.value = ''
  if (!username.value || !password.value) {
    error.value = 'Username and password are required.'
    return
  }
  try {
    await auth.login({ username: username.value, password: password.value })
    const redirect = route.query.redirect || '/dashboard'
    router.push(redirect)
  } catch (e) {
    error.value = e.displayMessage || 'Invalid credentials. Please try again.'
  }
}
</script>

<template>
  <div class="min-h-screen bg-gray-900 flex items-center justify-center p-4">
    <div class="w-full max-w-sm">
      <!-- Brand -->
      <div class="text-center mb-8">
        <div class="h-14 w-14 rounded-2xl bg-blue-600 flex items-center justify-center font-bold text-white text-xl mx-auto mb-3">
          DN
        </div>
        <h1 class="text-2xl font-bold text-white">DEVNEST</h1>
        <p class="text-gray-400 text-sm mt-1">Mobile Retail ERP & POS</p>
      </div>

      <!-- Card -->
      <div class="card p-6 shadow-2xl">
        <form @submit.prevent="handleLogin" class="space-y-4">
          <AppInput
            v-model="username"
            label="Username"
            placeholder="Enter username"
            autocomplete="username"
            required
            autofocus
          />
          <AppInput
            v-model="password"
            label="Password"
            type="password"
            placeholder="Enter password"
            autocomplete="current-password"
            required
          />

          <p v-if="error" role="alert" class="text-sm text-red-600 bg-red-50 border border-red-200 rounded-md px-3 py-2">
            {{ error }}
          </p>

          <AppButton
            type="submit"
            variant="primary"
            :loading="auth.loading"
            class="w-full"
          >
            Sign In
          </AppButton>
        </form>
      </div>

      <p class="text-center text-xs text-gray-600 mt-6">
        DEVNEST System v1.0 &nbsp;·&nbsp; All rights reserved
      </p>
    </div>
  </div>
</template>
