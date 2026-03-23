<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { useDark, useToggle } from '@vueuse/core'
import { useUserStore } from '@/stores/user'
import { categoryApi } from '@/api'
import type { Category } from '@/types'

const isDark = useDark()
const toggleDark = useToggle(isDark)

const userStore = useUserStore()
const route = useRoute()

const isMenuOpen = ref(false)
const categories = ref<Category[]>([])

onMounted(async () => {
  try {
    const { data } = await categoryApi.list()
    categories.value = data
  } catch (e) {
    console.error('Failed to load categories', e)
  }
})

function toggleMenu() {
  isMenuOpen.value = !isMenuOpen.value
}
</script>

<template>
  <div class="min-h-screen flex flex-col">
    <!-- 导航栏 -->
    <header class="sticky top-0 z-50 bg-white/80 dark:bg-slate-900/80 backdrop-blur-md border-b border-slate-100 dark:border-slate-800">
      <nav class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <!-- Logo -->
          <RouterLink to="/" class="flex items-center space-x-2">
            <div class="w-8 h-8 bg-gradient-to-br from-primary-500 to-violet-500 rounded-lg flex items-center justify-center">
              <span class="text-white font-bold text-lg">B</span>
            </div>
            <span class="text-xl font-bold text-gradient">MyBlog</span>
          </RouterLink>

          <!-- 桌面导航 -->
          <div class="hidden md:flex items-center space-x-8">
            <RouterLink
              to="/"
              class="text-slate-600 dark:text-slate-300 hover:text-primary-500 transition-colors"
              :class="{ 'text-primary-500': route.path === '/' }"
            >
              首页
            </RouterLink>
            <div class="relative group">
              <button class="text-slate-600 dark:text-slate-300 hover:text-primary-500 transition-colors">
                分类
              </button>
              <div class="absolute top-full left-0 mt-2 w-48 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200">
                <div class="bg-white dark:bg-slate-800 rounded-lg shadow-lg border border-slate-100 dark:border-slate-700 py-2">
                  <RouterLink
                    v-for="category in categories"
                    :key="category.id"
                    :to="`/category/${category.slug}`"
                    class="block px-4 py-2 text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700 hover:text-primary-500"
                  >
                    {{ category.name }}
                  </RouterLink>
                </div>
              </div>
            </div>
          </div>

          <!-- 右侧操作区 -->
          <div class="flex items-center space-x-4">
            <!-- 搜索 -->
            <RouterLink to="/search" class="p-2 text-slate-500 hover:text-primary-500 transition-colors">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </RouterLink>

            <!-- 深色模式切换 -->
            <button
              @click="toggleDark()"
              class="p-2 text-slate-500 hover:text-primary-500 transition-colors"
            >
              <svg v-if="isDark" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
              </svg>
              <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
              </svg>
            </button>

            <!-- 用户菜单 -->
            <div v-if="userStore.isLoggedIn" class="relative group">
              <button class="flex items-center space-x-2">
                <div class="w-8 h-8 bg-gradient-to-br from-primary-400 to-violet-400 rounded-full flex items-center justify-center">
                  <span class="text-white text-sm font-medium">
                    {{ userStore.user?.nickname?.[0] || userStore.user?.username[0] }}
                  </span>
                </div>
              </button>
              <div class="absolute right-0 top-full mt-2 w-48 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200">
                <div class="bg-white dark:bg-slate-800 rounded-lg shadow-lg border border-slate-100 dark:border-slate-700 py-2">
                  <RouterLink
                    v-if="userStore.isAdmin"
                    to="/admin"
                    class="block px-4 py-2 text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700"
                  >
                    后台管理
                  </RouterLink>
                  <button
                    @click="userStore.logout()"
                    class="w-full text-left px-4 py-2 text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700"
                  >
                    退出登录
                  </button>
                </div>
              </div>
            </div>
            <RouterLink
              v-else
              to="/login"
              class="btn-primary text-sm"
            >
              登录
            </RouterLink>

            <!-- 移动端菜单按钮 -->
            <button @click="toggleMenu" class="md:hidden p-2 text-slate-500">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path v-if="!isMenuOpen" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
                <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        <!-- 移动端菜单 -->
        <div v-if="isMenuOpen" class="md:hidden py-4 border-t border-slate-100 dark:border-slate-800">
          <RouterLink to="/" class="block py-2 text-slate-600 dark:text-slate-300">首页</RouterLink>
          <RouterLink
            v-for="category in categories"
            :key="category.id"
            :to="`/category/${category.slug}`"
            class="block py-2 text-slate-600 dark:text-slate-300"
          >
            {{ category.name }}
          </RouterLink>
        </div>
      </nav>
    </header>

    <!-- 主内容 -->
    <main class="flex-1">
      <router-view />
    </main>

    <!-- 页脚 -->
    <footer class="bg-white dark:bg-slate-800 border-t border-slate-100 dark:border-slate-700">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div class="flex flex-col md:flex-row justify-between items-center">
          <div class="text-slate-500 dark:text-slate-400 text-sm">
            © 2024 MyBlog. All rights reserved.
          </div>
          <div class="flex space-x-6 mt-4 md:mt-0">
            <a href="#" class="text-slate-400 hover:text-primary-500 transition-colors">
              <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
              </svg>
            </a>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>
