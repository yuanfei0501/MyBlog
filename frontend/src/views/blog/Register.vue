<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { authApi } from '@/api'

const router = useRouter()

const username = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const error = ref('')
const loading = ref(false)

async function handleRegister() {
  error.value = ''

  if (password.value !== confirmPassword.value) {
    error.value = '两次输入的密码不一致'
    return
  }

  if (password.value.length < 6) {
    error.value = '密码长度至少为6位'
    return
  }

  loading.value = true

  try {
    await authApi.register({
      username: username.value,
      email: email.value,
      password: password.value,
    })
    router.push('/login?registered=true')
  } catch (e: any) {
    error.value = e.response?.data?.detail || '注册失败，请稍后重试'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center px-4 py-12">
    <div class="max-w-md w-full">
      <!-- Logo -->
      <div class="text-center mb-8">
        <div class="w-16 h-16 bg-gradient-to-br from-primary-500 to-violet-500 rounded-2xl flex items-center justify-center mx-auto mb-4">
          <span class="text-white font-bold text-2xl">B</span>
        </div>
        <h1 class="text-2xl font-bold text-slate-900 dark:text-slate-100">创建账号</h1>
        <p class="text-slate-500 dark:text-slate-400 mt-2">加入我们的博客社区</p>
      </div>

      <!-- 注册表单 -->
      <form @submit.prevent="handleRegister" class="card p-8">
        <div v-if="error" class="mb-4 p-3 bg-red-50 dark:bg-red-900/30 text-red-600 dark:text-red-400 rounded-lg text-sm">
          {{ error }}
        </div>

        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">用户名</label>
            <input
              v-model="username"
              type="text"
              required
              minlength="3"
              class="input"
              placeholder="请输入用户名"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">邮箱</label>
            <input
              v-model="email"
              type="email"
              required
              class="input"
              placeholder="请输入邮箱"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">密码</label>
            <input
              v-model="password"
              type="password"
              required
              minlength="6"
              class="input"
              placeholder="请输入密码（至少6位）"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">确认密码</label>
            <input
              v-model="confirmPassword"
              type="password"
              required
              class="input"
              placeholder="请再次输入密码"
            />
          </div>

          <button
            type="submit"
            :disabled="loading"
            class="w-full btn-primary py-3 disabled:opacity-50"
          >
            <span v-if="loading" class="flex items-center justify-center">
              <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              注册中...
            </span>
            <span v-else>注册</span>
          </button>
        </div>

        <div class="mt-6 text-center text-sm text-slate-500 dark:text-slate-400">
          已有账号？
          <router-link to="/login" class="text-primary-500 hover:text-primary-600 font-medium">
            立即登录
          </router-link>
        </div>
      </form>
    </div>
  </div>
</template>
