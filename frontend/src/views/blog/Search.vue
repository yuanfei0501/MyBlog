<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { postApi } from '@/api'
import type { Post } from '@/types'

const route = useRoute()
const router = useRouter()

const keyword = ref('')
const posts = ref<Post[]>([])
const loading = ref(false)
const searched = ref(false)

onMounted(() => {
  if (route.query.q) {
    keyword.value = route.query.q as string
    search()
  }
})

watch(() => route.query.q, (newQuery) => {
  if (newQuery) {
    keyword.value = newQuery as string
    search()
  }
})

async function search() {
  if (!keyword.value.trim()) return

  loading.value = true
  searched.value = true
  router.push({ query: { q: keyword.value } })

  try {
    const { data } = await postApi.list({ keyword: keyword.value })
    posts.value = data.items
  } finally {
    loading.value = false
  }
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

function handleSubmit(e: Event) {
  e.preventDefault()
  search()
}
</script>

<template>
  <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
    <!-- 搜索框 -->
    <div class="mb-12">
      <form @submit="handleSubmit" class="relative">
        <input
          v-model="keyword"
          type="text"
          placeholder="搜索文章..."
          class="w-full px-6 py-4 pr-14 text-lg rounded-2xl border-2 border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 focus:border-primary-500 focus:ring-0 outline-none transition-colors"
        />
        <button
          type="submit"
          class="absolute right-4 top-1/2 -translate-y-1/2 p-2 text-slate-400 hover:text-primary-500"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </button>
      </form>
    </div>

    <!-- 搜索结果 -->
    <div v-if="loading" class="flex justify-center py-20">
      <div class="animate-spin rounded-full h-12 w-12 border-4 border-primary-500 border-t-transparent"></div>
    </div>

    <div v-else-if="searched">
      <div v-if="posts.length === 0" class="text-center py-20">
        <p class="text-slate-500 dark:text-slate-400">未找到相关文章</p>
      </div>

      <div v-else>
        <p class="text-slate-500 dark:text-slate-400 mb-8">
          找到 {{ posts.length }} 篇相关文章
        </p>

        <div class="space-y-6">
          <router-link
            v-for="post in posts"
            :key="post.id"
            :to="`/post/${post.slug}`"
            class="card p-6 flex gap-6 hover:shadow-lg transition-shadow group"
          >
            <div v-if="post.cover_image" class="w-32 h-24 flex-shrink-0 rounded-lg overflow-hidden">
              <img
                :src="post.cover_image"
                :alt="post.title"
                class="w-full h-full object-cover"
              />
            </div>
            <div class="flex-1">
              <h2 class="text-xl font-bold text-slate-800 dark:text-slate-100 mb-2 group-hover:text-primary-500 transition-colors">
                {{ post.title }}
              </h2>
              <p class="text-slate-500 dark:text-slate-400 text-sm mb-2 line-clamp-2">
                {{ post.summary || '点击查看详情...' }}
              </p>
              <p class="text-slate-400 text-sm">{{ formatDate(post.created_at) }}</p>
            </div>
          </router-link>
        </div>
      </div>
    </div>

    <div v-else class="text-center py-20">
      <p class="text-slate-500 dark:text-slate-400">输入关键词搜索文章</p>
    </div>
  </div>
</template>
