<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { postApi, tagApi } from '@/api'
import type { Post, Tag } from '@/types'

const route = useRoute()
const tag = ref<Tag | null>(null)
const posts = ref<Post[]>([])
const loading = ref(true)

onMounted(async () => {
  await loadTag()
})

watch(() => route.params.slug, async () => {
  await loadTag()
})

async function loadTag() {
  loading.value = true
  try {
    const { data: tags } = await tagApi.list()
    tag.value = tags.find(t => t.slug === route.params.slug) || null

    if (tag.value) {
      const { data } = await postApi.list({ tag_id: tag.value.id })
      posts.value = data.items
    }
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
</script>

<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
    <div v-if="loading" class="flex justify-center py-20">
      <div class="animate-spin rounded-full h-12 w-12 border-4 border-primary-500 border-t-transparent"></div>
    </div>

    <template v-else-if="tag">
      <div class="text-center mb-12">
        <h1 class="text-3xl font-bold text-slate-900 dark:text-slate-100">
          #{{ tag.name }}
        </h1>
      </div>

      <div v-if="posts.length === 0" class="text-center py-20">
        <p class="text-slate-500 dark:text-slate-400">该标签下暂无文章</p>
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        <router-link
          v-for="post in posts"
          :key="post.id"
          :to="`/post/${post.slug}`"
          class="card-hover overflow-hidden group"
        >
          <div class="aspect-video bg-gradient-to-br from-primary-100 to-violet-100 dark:from-primary-900/30 dark:to-violet-900/30 relative overflow-hidden">
            <img
              v-if="post.cover_image"
              :src="post.cover_image"
              :alt="post.title"
              class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
            />
          </div>
          <div class="p-6">
            <h2 class="text-xl font-bold text-slate-800 dark:text-slate-100 mb-2 line-clamp-2 group-hover:text-primary-500 transition-colors">
              {{ post.title }}
            </h2>
            <p class="text-slate-500 text-sm">{{ formatDate(post.created_at) }}</p>
          </div>
        </router-link>
      </div>
    </template>

    <div v-else class="text-center py-20">
      <p class="text-slate-500 dark:text-slate-400">标签不存在</p>
      <router-link to="/" class="text-primary-500 mt-4 inline-block">返回首页</router-link>
    </div>
  </div>
</template>
