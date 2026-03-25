<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { userApi } from '@/api'
import type { User } from '@/types'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const users = ref<User[]>([])
const loading = ref(true)

onMounted(async () => {
  await loadUsers()
})

async function loadUsers() {
  try {
    const { data } = await userApi.list()
    users.value = data
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

function formatDate(date: string) {
  return new Date(date).toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

async function toggleStatus(userId: number) {
  if (!confirm('确定更改此用户状态吗？')) return
  try {
    await userApi.toggleStatus(userId)
    await loadUsers()
  } catch (e: any) {
    alert(e.response?.data?.detail || '操作失败')
  }
}

async function updateRole(userId: number, role: string) {
  try {
    await userApi.updateRole(userId, role)
    await loadUsers()
  } catch (e: any) {
    alert(e.response?.data?.detail || '操作失败')
  }
}
</script>

<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold text-slate-800 dark:text-slate-100">用户管理</h1>
    </div>

    <div v-if="loading" class="flex justify-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-4 border-primary-500 border-t-transparent"></div>
    </div>

    <div v-else class="space-y-4">
      <div
        v-for="user in users"
        :key="user.id"
        class="card p-6 hover:shadow-md transition-shadow"
      >
        <div class="flex justify-between items-start">
          <!-- 用户信息 -->
          <div class="flex items-center gap-4">
            <div class="w-12 h-12 rounded-full bg-gradient-to-br from-primary-400 to-violet-400 flex items-center justify-center">
              <span class="text-white text-lg font-bold">{{ user.username?.[0]?.toUpperCase() }}</span>
            </div>
            <div>
              <div class="flex items-center gap-2">
                <span class="font-bold text-slate-800 dark:text-slate-100">
                  {{ user.nickname || user.username }}
                </span>
                <span
                  :class="[
                    'px-2 py-0.5 text-xs font-medium rounded',
                    user.role === 'admin'
                      ? 'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400'
                      : 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400'
                  ]"
                >
                  {{ user.role === 'admin' ? '管理员' : '用户' }}
                </span>
                <span
                  :class="[
                    'px-2 py-0.5 text-xs font-medium rounded',
                    user.is_active
                      ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
                      : 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
                  ]"
                >
                  {{ user.is_active ? '正常' : '已禁用' }}
                </span>
              </div>
              <div class="flex items-center gap-4 mt-1 text-sm text-slate-500 dark:text-slate-400">
                <span>{{ user.email }}</span>
                <span>注册于 {{ formatDate(user.created_at) }}</span>
              </div>
            </div>
          </div>

          <!-- 操作按钮 -->
          <div class="flex gap-3">
            <button
              v-if="user.role !== 'admin'"
              @click="updateRole(user.id, 'admin')"
              class="px-5 py-2 bg-purple-500 hover:bg-purple-600 text-white rounded-lg font-medium transition-colors"
            >
              设为管理员
            </button>
            <button
              @click="toggleStatus(user.id)"
              :disabled="user.id === userStore.user?.id"
              :class="[
                'px-5 py-2 rounded-lg font-medium transition-colors',
                user.is_active
                  ? 'bg-red-500 hover:bg-red-600 text-white'
                  : 'bg-green-500 hover:bg-green-600 text-white',
                user.id === userStore.user?.id ? 'opacity-50 cursor-not-allowed' : ''
              ]"
            >
              {{ user.is_active ? '禁用' : '启用' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
