<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { postApi } from '@/api'
import type { Post } from '@/types'

const posts = ref<Post[]>([])
const loading = ref(true)
const page = ref(1)
const totalPages = ref(1)

onMounted(async () => {
  await loadPosts()
})

async function loadPosts() {
  loading.value = true
  try {
    const { data } = await postApi.list({ page: page.value, page_size: 9 })
    posts.value = data.items
    totalPages.value = data.total_pages
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

function changePage(newPage: number) {
  page.value = newPage
  loadPosts()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}
</script>

<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
    <!-- Hero Section -->
    <div class="text-center mb-16">
      <h1 class="text-4xl md:text-5xl font-bold mb-4">
        <span class="text-gradient">探索与分享</span>
      </h1>
      <p class="text-slate-600 dark:text-slate-400 text-lg max-w-2xl mx-auto">
        记录技术成长、分享思考与见解
      </p>
    </div>

    <!-- 文章列表 -->
    <div v-if="loading" class="flex justify-center py-20">
      <div class="animate-spin rounded-full h-12 w-12 border-4 border-primary-500 border-t-transparent"></div>
    </div>

    <div v-else-if="posts.length === 0" class="text-center py-20">
      <p class="text-slate-500 dark:text-slate-400">暂无文章</p>
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
      <router-link
        v-for="post in posts"
        :key="post.id"
        :to="`/post/${post.slug}`"
        class="card-hover overflow-hidden group"
      >
        <!-- 封面图 -->
        <div class="aspect-video bg-gradient-to-br from-primary-100 to-violet-100 dark:from-primary-900/30 dark:to-violet-900/30 relative overflow-hidden">
          <img
            v-if="post.cover_image"
            :src="post.cover_image"
            :alt="post.title"
            class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
          />
          <div v-else class="w-full h-full flex items-center justify-center">
            <span class="text-4xl opacity-50">📝</span>
          </div>
          <!-- 置顶标记 -->
          <div
            v-if="post.is_top"
            class="absolute top-3 left-3 px-2 py-1 bg-accent-rose text-white text-xs rounded"
          >
            置顶
          </div>
        </div>

        <!-- 文章信息 -->
        <div class="p-6">
          <!-- 分类 -->
          <div v-if="post.category" class="mb-3">
            <span class="text-primary-500 text-sm font-medium">
              {{ post.category.name }}
            </span>
          </div>

          <!-- 标题 -->
          <h2 class="text-xl font-bold text-slate-800 dark:text-slate-100 mb-3 line-clamp-2 group-hover:text-primary-500 transition-colors">
            {{ post.title }}
          </h2>

          <!-- 摘要 -->
          <p class="text-slate-600 dark:text-slate-400 text-sm mb-4 line-clamp-2">
            {{ post.summary || '点击查看详情...' }}
          </p>

          <!-- 标签 -->
          <div class="flex flex-wrap gap-2 mb-4">
            <span
              v-for="tag in post.tags.slice(0, 3)"
              :key="tag.id"
              class="px-2 py-1 bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 text-xs rounded"
            >
              #{{ tag.name }}
            </span>
          </div>

          <!-- 底部信息 -->
          <div class="flex items-center justify-between text-sm text-slate-500 dark:text-slate-400">
            <div class="flex items-center space-x-2">
              <div class="w-6 h-6 bg-gradient-to-br from-primary-400 to-violet-400 rounded-full flex items-center justify-center">
                <span class="text-white text-xs">
                  {{ post.author.nickname?.[0] || post.author.username[0] }}
                </span>
              </div>
              <span>{{ post.author.nickname || post.author.username }}</span>
            </div>
            <div class="flex items-center space-x-3">
              <span>{{ formatDate(post.created_at) }}</span>
              <span class="flex items-center space-x-1">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
                <span>{{ post.view_count }}</span>
              </span>
            </div>
          </div>
        </div>
      </router-link>
    </div>

    <!-- 分页 -->
    <div v-if="totalPages > 1" class="flex justify-center mt-12 space-x-2">
      <button
        @click="changePage(page - 1)"
        :disabled="page === 1"
        class="px-4 py-2 rounded-lg border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300 disabled:opacity-50 disabled:cursor-not-allowed hover:border-primary-500 hover:text-primary-500 transition-colors"
      >
        上一页
      </button>
      <button
        v-for="p in totalPages"
        :key="p"
        @click="changePage(p)"
        :class="[
          'px-4 py-2 rounded-lg transition-colors',
          p === page
            ? 'bg-primary-500 text-white'
            : 'border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300 hover:border-primary-500 hover:text-primary-500'
        ]"
      >
        {{ p }}
      </button>
      <button
        @click="changePage(page + 1)"
        :disabled="page === totalPages"
        class="px-4 py-2 rounded-lg border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300 disabled:opacity-50 disabled:cursor-not-allowed hover:border-primary-500 hover:text-primary-500 transition-colors"
      >
        下一页
      </button>
    </div>
  </div>
</template>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
