<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { adminApi } from '@/api'
import type { DashboardData } from '@/types'

const data = ref<DashboardData | null>(null)
const loading = ref(true)

onMounted(async () => {
  try {
    const { data: res } = await adminApi.getDashboard()
    data.value = res
  } finally {
    loading.value = false
  }
})

const stats = [
  { key: 'posts', label: '文章总数', icon: '📝', color: 'from-blue-500 to-blue-600' },
  { key: 'users', label: '用户总数', icon: '👥', color: 'from-green-500 to-green-600' },
  { key: 'comments', label: '评论总数', icon: '💬', color: 'from-purple-500 to-purple-600' },
  { key: 'media', label: '媒体文件', icon: '🖼️', color: 'from-orange-500 to-orange-600' },
]
</script>

<template>
  <div>
    <h1 class="text-2xl font-bold text-slate-800 dark:text-slate-100 mb-8">仪表盘</h1>

    <div v-if="loading" class="flex justify-center py-20">
      <div class="animate-spin rounded-full h-12 w-12 border-4 border-primary-500 border-t-transparent"></div>
    </div>

    <template v-else-if="data">
      <!-- 统计卡片 -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div class="card p-6">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-slate-500 dark:text-slate-400 text-sm">文章总数</p>
              <p class="text-3xl font-bold text-slate-800 dark:text-slate-100 mt-1">{{ data.posts.total }}</p>
              <p class="text-sm text-slate-400 mt-1">已发布: {{ data.posts.published }}</p>
            </div>
            <div class="w-12 h-12 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center">
              <span class="text-2xl">📝</span>
            </div>
          </div>
        </div>

        <div class="card p-6">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-slate-500 dark:text-slate-400 text-sm">用户总数</p>
              <p class="text-3xl font-bold text-slate-800 dark:text-slate-100 mt-1">{{ data.users.total }}</p>
            </div>
            <div class="w-12 h-12 bg-gradient-to-br from-green-500 to-green-600 rounded-xl flex items-center justify-center">
              <span class="text-2xl">👥</span>
            </div>
          </div>
        </div>

        <div class="card p-6">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-slate-500 dark:text-slate-400 text-sm">评论总数</p>
              <p class="text-3xl font-bold text-slate-800 dark:text-slate-100 mt-1">{{ data.comments.total }}</p>
              <p class="text-sm text-slate-400 mt-1">待审核: {{ data.comments.pending }}</p>
            </div>
            <div class="w-12 h-12 bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl flex items-center justify-center">
              <span class="text-2xl">💬</span>
            </div>
          </div>
        </div>

        <div class="card p-6">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-slate-500 dark:text-slate-400 text-sm">媒体文件</p>
              <p class="text-3xl font-bold text-slate-800 dark:text-slate-100 mt-1">{{ data.media.total }}</p>
            </div>
            <div class="w-12 h-12 bg-gradient-to-br from-orange-500 to-orange-600 rounded-xl flex items-center justify-center">
              <span class="text-2xl">🖼️</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 最近文章和评论 -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- 最近文章 -->
        <div class="card p-6">
          <h2 class="text-lg font-bold text-slate-800 dark:text-slate-100 mb-4">最近文章</h2>
          <div class="space-y-4">
            <div
              v-for="post in data.recent_posts"
              :key="post.id"
              class="flex items-center justify-between py-2 border-b border-slate-100 dark:border-slate-700 last:border-0"
            >
              <div class="flex-1 min-w-0">
                <p class="text-slate-800 dark:text-slate-200 font-medium truncate">{{ post.title }}</p>
                <p class="text-slate-400 text-sm">{{ post.view_count }} 阅读</p>
              </div>
              <span
                :class="[
                  'px-2 py-1 text-xs rounded',
                  post.status === 'published'
                    ? 'bg-green-100 text-green-600 dark:bg-green-900/30 dark:text-green-400'
                    : 'bg-yellow-100 text-yellow-600 dark:bg-yellow-900/30 dark:text-yellow-400'
                ]"
              >
                {{ post.status === 'published' ? '已发布' : '草稿' }}
              </span>
            </div>
          </div>
        </div>

        <!-- 最近评论 -->
        <div class="card p-6">
          <h2 class="text-lg font-bold text-slate-800 dark:text-slate-100 mb-4">最近评论</h2>
          <div class="space-y-4">
            <div
              v-for="comment in data.recent_comments"
              :key="comment.id"
              class="py-2 border-b border-slate-100 dark:border-slate-700 last:border-0"
            >
              <p class="text-slate-600 dark:text-slate-300 text-sm">{{ comment.content }}</p>
              <p class="text-slate-400 text-xs mt-1">
                {{ new Date(comment.created_at).toLocaleDateString('zh-CN') }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>
