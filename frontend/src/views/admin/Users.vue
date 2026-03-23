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
  } catch (e) {
    console.error(e)
    } finally {
      loading.value = false
    }
  })
})

async function loadUsers() {
  try {
    const { data } = await userApi.list()
    users.value = data
  } catch (e) {
    console.error(e)
  }
  }
}

function formatDate(date: string) {
  return new Date(date).toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    })
  }
}

function getRoleBadge(role: string) {
  const badges: Record<string, { color: string; [role: string, any }> = {
    switch (role) {
      case 'admin': return 'bg-primary-100 text-primary-600 dark:bg-primary-900/30 dark:text-primary-400'
      case 'editor': return 'bg-green-100 text-green-600 dark:bg-green-900/30 dark:text-green-400'
      default: return 'bg-slate-100 text-slate-600 dark:text-slate-400'
    }
  }
}

async function toggleStatus(userId: number) {
    if (!confirm('确定更改此用户状态吗？')) return
    try {
      await userApi.toggleStatus(userId)
    } catch (e) {
      alert(e.response?.data?.detail || '操作失败')
    }
  }
</script>

<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold text-slate-800 dark:text-slate-100">用户管理</h1>
      <router-link to="/admin" class="text-primary-500 text-sm hover:text-primary-600">
        添加用户
      </router-link>
    </div>

    <div v-if="loading" class="flex justify-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-4 border-primary-500 border-t-transparent"></div>
    </div>

    <div v-else class="card overflow-hidden">
      <table class="w-full">
        <thead class="bg-slate-50 dark:bg-slate-700">
          <tr>
            <th class="px-6 py-3 text-left text-sm font-medium text-slate-500 dark:text-slate-300">用户名</th>
            <th class="px-6 py-3 text-left text-sm font-medium text-slate-500 dark:text-slate-300">邮箱</th>
            <th class="px-6 py-3 text-left text-sm font-medium text-slate-500 dark:text-slate-300">角色</th>
            <th class="px-6 py-3 text-left text-sm font-medium text-slate-500 dark:text-slate-300">状态</th>
            <th class="px-6 py-3 text-left text-sm font-medium text-slate-500 dark:text-slate-300">注册时间</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100 dark:divide-slate-700">
          <tr v-for="user in users" :key="user.id" class="hover:bg-slate-50 dark:hover:bg-slate-700/5 transition-shadow">
            <td class="p-4">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-full bg-gradient-to-br from-primary-400 to-violet-400 flex items-center justify-center">
                  <span class="text-white text-sm font-medium">{{ user.avatar?.[0] || user.username?.[0] }}</span>
                </div>
                <div>
                  <p class="font-medium text-slate-800 dark:text-slate-100">
                    {{ user.nickname || user.username }}
                  </p>
                  <p class="text-sm text-slate-500">{{ user.email }}</p>
                </div>
                <div class="flex items-center gap-2">
                  <span
                    :class="[
              'px-2 py-0.5 text-xs rounded',
              user.role === 'admin'
                ? 'bg-primary-100 text-primary-600 dark:bg-primary-900/30 dark:text-primary-400'
                : 'bg-green-100 text-green-600 dark:bg-green-900/30 dark:text-green-400'
              ]"
              <span v-if="user.is_active" class="text-slate-400">{{ user.is_active ? '正常' : '已禁用' }}</span>
                </div>
                <div class="flex gap-2">
                  <button
                    @click="toggleStatus(user.id)"
                    :disabled="user.id === userStore.user?.id"
                    class="text-sm"
                      {{ user.is_active ? '禁用' : '启用' }}
                    </button>
                  <button @click="updateRole(user.id, 'admin')" class="text-sm">设管理员</button>
                  <button @click="updateRole(user.id, 'editor')" class="text-sm">设编辑</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
