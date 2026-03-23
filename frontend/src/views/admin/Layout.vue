<script setup lang="ts">
import { ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const route = useRoute()
const router = useRouter()
const isSidebarOpen = ref(true)

const menuItems = [
  { path: '/admin', name: '仪表盘', icon: 'dashboard' },
  { path: '/admin/posts', name: '文章管理', icon: 'post' },
  { path: '/admin/categories', name: '分类管理', icon: 'category' },
  { path: '/admin/tags', name: '标签管理', icon: 'tag' },
  { path: '/admin/comments', name: '评论管理', icon: 'comment' },
  { path: '/admin/media', name: '媒体库', icon: 'media' },
  { path: '/admin/users', name: '用户管理', icon: 'user' },
  { path: '/admin/settings', name: '系统设置', icon: 'setting' },
]

function handleLogout() {
  userStore.logout()
  router.push('/login')
}
</script>

<template>
  <div class="min-h-screen flex bg-slate-100 dark:bg-slate-900">
    <!-- 侧边栏 -->
    <aside
      :class="[
        'fixed inset-y-0 left-0 z-50 w-64 bg-white dark:bg-slate-800 border-r border-slate-200 dark:border-slate-700 transform transition-transform duration-300 lg:translate-x-0 lg:static',
        isSidebarOpen ? 'translate-x-0' : '-translate-x-full'
      ]"
    >
      <!-- Logo -->
      <div class="h-16 flex items-center px-6 border-b border-slate-200 dark:border-slate-700">
        <router-link to="/" class="flex items-center space-x-2">
          <div class="w-8 h-8 bg-gradient-to-br from-primary-500 to-violet-500 rounded-lg flex items-center justify-center">
            <span class="text-white font-bold">B</span>
          </div>
          <span class="text-lg font-bold text-slate-800 dark:text-slate-100">MyBlog</span>
        </router-link>
      </div>

      <!-- 导航菜单 -->
      <nav class="p-4 space-y-1">
        <router-link
          v-for="item in menuItems"
          :key="item.path"
          :to="item.path"
          :class="[
            'flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors',
            route.path === item.path
              ? 'bg-primary-50 dark:bg-primary-900/30 text-primary-600 dark:text-primary-400'
              : 'text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-700'
          ]"
        >
          <span>{{ item.name }}</span>
        </router-link>
      </nav>
    </aside>

    <!-- 主内容区 -->
    <div class="flex-1 flex flex-col min-w-0">
      <!-- 顶部栏 -->
      <header class="h-16 bg-white dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700 flex items-center justify-between px-6">
        <button
          @click="isSidebarOpen = !isSidebarOpen"
          class="lg:hidden p-2 text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>

        <div class="flex items-center space-x-4">
          <router-link to="/" class="text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200">
            访问前台
          </router-link>
          <div class="flex items-center space-x-3">
            <div class="w-8 h-8 bg-gradient-to-br from-primary-400 to-violet-400 rounded-full flex items-center justify-center">
              <span class="text-white text-sm">{{ userStore.user?.username?.[0] }}</span>
            </div>
            <button @click="handleLogout" class="text-slate-500 hover:text-red-500">
              退出
            </button>
          </div>
        </div>
      </header>

      <!-- 页面内容 -->
      <main class="flex-1 p-6 overflow-auto">
        <router-view />
      </main>
    </div>

    <!-- 遮罩层 -->
    <div
      v-if="isSidebarOpen"
      @click="isSidebarOpen = false"
      class="fixed inset-0 bg-black/50 z-40 lg:hidden"
    ></div>
  </div>
</template>
