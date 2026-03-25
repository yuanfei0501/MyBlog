<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { postApi } from '@/api'
import type { Post } from '@/types'

const posts = ref<Post[]>([])
const loading = ref(true)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const totalPages = ref(0)

onMounted(async () => {
  await loadPosts()
})

async function loadPosts() {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      status: '',
    }
    const { data } = await postApi.list(params)
    posts.value = data.items
    total.value = data.total
    totalPages.value = data.total_pages
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

async function deletePost(id: number) {
  if (!confirm('确定删除这篇文章吗？')) return
  try {
    await postApi.delete(id)
    await loadPosts()
  } catch (e) {
    console.error(e)
  }
}
</script>

<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold text-slate-800 dark:text-slate-100">文章管理</h1>
      <div class="flex items-center gap-4">
        <router-link
          to="/admin/posts/new"
          class="px-5 py-2 bg-primary-500 hover:bg-primary-600 text-white rounded-lg font-medium transition-colors"
        >
          新写文章
        </router-link>
        <div class="flex items-center gap-2">
          <span class="text-slate-500 dark:text-slate-400">共 {{ total }} 篇文章</span>
          <span class="text-slate-400">| 第 {{ currentPage }} / {{ totalPages }} 页</span>
        </div>
      </div>
    </div>

    <div v-if="loading" class="flex justify-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-4 border-primary-500 border-t-transparent"></div>
    </div>

    <div v-else class="space-y-4">
      <div
        v-for="post in posts"
        :key="post.id"
        class="card p-6 hover:shadow-md transition-shadow"
      >
        <div class="flex justify-between items-start mb-4">
          <div class="flex-1 min-w-0">
            <h3 class="font-bold text-lg text-slate-800 dark:text-slate-100 truncate">{{ post.title }}</h3>
          </div>
          <div class="flex gap-3 ml-4">
            <router-link
              :to="`/admin/posts/${post.id}/edit`"
              class="px-5 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg font-medium transition-colors"
            >
              编辑
            </router-link>
            <button
              @click="deletePost(post.id)"
              class="px-5 py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg font-medium transition-colors"
            >
              删除
            </button>
          </div>
        </div>
        <div class="flex items-center gap-4 text-sm">
          <span
            :class="[
              'px-3 py-1 text-sm font-medium rounded-full',
              post.status === 'published'
                ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
                : 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400'
            ]"
          >
            {{ post.status === 'published' ? '已发布' : '草稿' }}
          </span>
          <span class="text-slate-500 dark:text-slate-400">{{ post.category?.name || '未分类' }}</span>
          <span class="text-slate-400">{{ post.view_count }} 阅读</span>
          <span class="text-slate-400">{{ formatDate(post.created_at) }}</span>
        </div>
      </div>

      <div v-if="posts.length === 0" class="text-center py-12 text-slate-500 dark:text-slate-400">
        暂无文章
      </div>
    </div>
  </div>
</template>
