<script setup>
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useUiStore } from '@/stores/ui'
import AppButton from '@/components/ui/AppButton.vue'

const auth = useAuthStore()
const ui = useUiStore()

const testUsers = [
  { username: 'owner', password: 'owner123', role: 'Shop Owner', icon: '👑' },
  { username: 'cashier', password: 'cashier123', role: 'Salesperson', icon: '💳' },
  { username: 'technician', password: 'tech123', role: 'Technician', icon: '🔧' },
]

const switching = ref(false)

async function switchRole(user) {
  switching.value = true
  try {
    // Logout current user
    await auth.logout()

    // Login as new user
    await auth.login(user.username, user.password)

    ui.toastSuccess?.(`Switched to ${user.role} role`)
  } catch (e) {
    ui.toastError?.('Failed to switch role')
  } finally {
    switching.value = false
  }
}

const currentUser = auth.user
</script>

<template>
  <div class="role-switcher">
    <!-- Header -->
    <div class="role-switcher-header">
      <h4>Quick Role Switch</h4>
      <p class="text-xs text-gray-500">Testing & Development Only</p>
    </div>

    <!-- Current Role -->
    <div class="current-role">
      <span class="role-badge">
        {{ currentUser?.role_display || 'Not logged in' }}
      </span>
    </div>

    <!-- Role Buttons -->
    <div class="role-buttons">
      <AppButton
        v-for="user in testUsers"
        :key="user.username"
        variant="secondary"
        size="sm"
        class="role-button"
        :class="{ active: currentUser?.username === user.username }"
        :loading="switching"
        @click="switchRole(user)"
      >
        <span class="role-icon">{{ user.icon }}</span>
        <span class="role-text">{{ user.role }}</span>
      </AppButton>
    </div>

    <!-- Test Credentials Info -->
    <div class="credentials-info">
      <details>
        <summary>Test Credentials</summary>
        <div class="credentials-list">
          <div v-for="user in testUsers" :key="user.username" class="credential-item">
            <code>{{ user.username }}</code>
            <code class="password">{{ user.password }}</code>
          </div>
        </div>
      </details>
    </div>
  </div>
</template>

<style scoped>
.role-switcher {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 8px;
  padding: 16px;
  color: white;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.role-switcher-header {
  margin-bottom: 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  padding-bottom: 8px;
}

.role-switcher-header h4 {
  margin: 0 0 4px 0;
  font-size: 14px;
  font-weight: 600;
}

.role-switcher-header p {
  margin: 0;
  color: rgba(255, 255, 255, 0.7);
}

.current-role {
  margin: 12px 0;
  text-align: center;
}

.role-badge {
  display: inline-block;
  background: rgba(255, 255, 255, 0.2);
  padding: 6px 12px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.role-buttons {
  display: grid;
  grid-template-columns: 1fr;
  gap: 8px;
  margin: 12px 0;
}

.role-button {
  display: flex;
  align-items: center;
  gap: 8px;
  justify-content: center;
  transition: all 0.2s ease;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
}

.role-button:hover {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.4);
}

.role-button.active {
  background: rgba(255, 255, 255, 0.3);
  border-color: white;
  font-weight: 600;
}

.role-icon {
  font-size: 16px;
}

.role-text {
  font-size: 13px;
}

.credentials-info {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.2);
}

.credentials-info details {
  cursor: pointer;
}

.credentials-info summary {
  font-size: 12px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.8);
  user-select: none;
}

.credentials-info summary:hover {
  color: white;
}

.credentials-list {
  margin-top: 8px;
  display: grid;
  gap: 6px;
  font-size: 11px;
}

.credential-item {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  align-items: center;
  background: rgba(0, 0, 0, 0.2);
  padding: 6px 8px;
  border-radius: 4px;
}

.credential-item code {
  background: rgba(0, 0, 0, 0.3);
  padding: 2px 6px;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
  color: #e2e8f0;
  word-break: break-all;
}

.credential-item code.password {
  text-align: right;
}

@media (max-width: 768px) {
  .role-buttons {
    grid-template-columns: 1fr 1fr;
  }

  .role-button {
    flex-direction: column;
  }

  .role-icon {
    order: -1;
  }
}
</style>
