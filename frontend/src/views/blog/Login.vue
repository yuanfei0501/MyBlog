<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function handleLogin() {
  error.value = ''
  loading.value = true

  try {
    await userStore.login(username.value, password.value)
    const redirect = route.query.redirect as string
    router.push(redirect || '/')
  } catch (e: any) {
    error.value = e.response?.data?.detail || '登录失败，请检查用户名和密码'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center px-4">
    <div class="max-w-md w-full">
      <!-- Logo -->
      <div class="text-center mb-8">
        <div class="w-16 h-16 bg-gradient-to-br from-primary-500 to-violet-500 rounded-2xl flex items-center justify-center mx-auto mb-4">
          <span class="text-white font-bold text-2xl">B</span>
        </div>
        <h1 class="text-2xl font-bold text-slate-900 dark:text-slate-100">欢迎回来</h1>
        <p class="text-slate-500 dark:text-slate-400 mt-2">登录你的博客账号</p>
      </div>

      <!-- 登录表单 -->
      <form @submit.prevent="handleLogin" class="card p-8">
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
              class="input"
              placeholder="请输入用户名"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">密码</label>
            <input
              v-model="password"
              type="password"
              required
              class="input"
              placeholder="请输入密码"
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
              登录中...
            </span>
            <span v-else>登录</span>
          </button>
        </div>

        <div class="mt-6 text-center text-sm text-slate-500 dark:text-slate-400">
          还没有账号？
          <router-link to="/register" class="text-primary-500 hover:text-primary-600 font-medium">
            立即注册
          </router-link>
        </div>
      </form>
    </div>
  </div>
</template>
