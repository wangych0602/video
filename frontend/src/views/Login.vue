<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Lock, MonitorPlay, User } from 'lucide-vue-next'
import { login } from '@/api/auth'
import { useUserStore } from '@/stores/user'

const { t } = useI18n()

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const form = reactive({
  username: '',
  password: '',
})
const loading = ref(false)

async function handleLogin() {
  if (!form.username || !form.password) {
    ElMessage.warning(t('login.warn'))
    return
  }

  loading.value = true
  try {
    const result = await login(form.username, form.password)
    userStore.login(result.token, {
      username: result.user.username,
      role: result.user.role,
      school: result.user.school ? String(result.user.school) : '',
    })
    ElMessage.success(t('login.success'))
    const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : '/'
    void router.push(redirect)
  } catch {
    // handled by request interceptor
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-page">
    <div class="login-panel">
      <div class="login-brand">
        <MonitorPlay :size="28" />
        <span>{{ t('login.brand') }}</span>
      </div>
      <h1>{{ t('login.title') }}</h1>
      <p class="login-tip">{{ t('login.tip') }}</p>
      <el-form :model="form" label-position="top" @submit.prevent="handleLogin">
        <el-form-item :label="t('login.account')">
          <el-input v-model="form.username" :placeholder="t('login.accountPlaceholder')" :prefix-icon="User" />
        </el-form-item>
        <el-form-item :label="t('login.password')">
          <el-input
            v-model="form.password"
            type="password"
            show-password
            :placeholder="t('login.passwordPlaceholder')"
            :prefix-icon="Lock"
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        <el-button type="primary" class="login-button" :loading="loading" @click="handleLogin">
          {{ t('login.button') }}
        </el-button>
      </el-form>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background: var(--platform-bg);
}

.login-panel {
  width: 100%;
  max-width: 420px;
  padding: 32px;
  background: var(--platform-panel);
  border: 1px solid var(--platform-line);
  border-radius: 8px;
}

.login-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 24px;
  color: var(--platform-primary);
  font-size: 17px;
  font-weight: 700;
}

.login-panel h1 {
  margin: 0 0 6px;
  font-size: 26px;
  letter-spacing: 0;
}

.login-tip {
  margin: 0 0 20px;
  color: var(--platform-muted);
  font-size: 14px;
}

.login-button {
  width: 100%;
}
</style>
