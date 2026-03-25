<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { commentApi } from '@/api'
import type { Comment } from '@/types'

const comments = ref<Comment[]>([])
const loading = ref(true)
const filter = ref<'all' | 'pending' | 'approved'>('all')

onMounted(async () => {
  await loadComments()
})

async function loadComments() {
  loading.value = true
  try {
    const { data } = await commentApi.listAll()
    comments.value = data
  } catch (e) {
    console.error(e)
    comments.value = []
  } finally {
    loading.value = false
  }
}

const filteredComments = computed(() => {
  if (filter.value === 'all') return comments.value
  return comments.value.filter(c => c.status === filter.value)
})

const pendingCount = computed(() => comments.value.filter(c => c.status === 'pending').length)

async function approve(id: number) {
  try {
    await commentApi.approve(id)
    await loadComments()
  } catch (e: any) {
    alert(e.response?.data?.detail || '操作失败')
  }
}

async function handleDelete(id: number) {
  if (!confirm('确定删除该评论吗？')) return
  try {
    await commentApi.delete(id)
    await loadComments()
  } catch (e: any) {
    alert(e.response?.data?.detail || '删除失败')
  }
}

function formatDate(date: string) {
  return new Date(date).toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold text-slate-800 dark:text-slate-100">评论管理</h1>
      <div class="flex gap-2">
        <button
          @click="filter = 'all'"
          :class="[
            'px-4 py-2 rounded-lg text-sm font-medium transition-colors',
            filter === 'all'
              ? 'bg-primary-500 text-white'
              : 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600'
          ]"
        >
          全部 ({{ comments.length }})
        </button>
        <button
          @click="filter = 'pending'"
          :class="[
            'px-4 py-2 rounded-lg text-sm font-medium transition-colors',
            filter === 'pending'
              ? 'bg-yellow-500 text-white'
              : 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600'
          ]"
        >
          待审核 ({{ pendingCount }})
        </button>
        <button
          @click="filter = 'approved'"
          :class="[
            'px-4 py-2 rounded-lg text-sm font-medium transition-colors',
            filter === 'approved'
              ? 'bg-green-500 text-white'
              : 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600'
          ]"
        >
          已通过 ({{ comments.length - pendingCount }})
        </button>
      </div>
    </div>

    <div v-if="loading" class="flex justify-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-4 border-primary-500 border-t-transparent"></div>
    </div>

    <div v-else-if="filteredComments.length === 0" class="card p-12 text-center text-slate-500">
      暂无评论
    </div>

    <div v-else class="space-y-4">
      <div
        v-for="comment in filteredComments"
        :key="comment.id"
        class="card p-6 hover:shadow-md transition-shadow"
      >
        <!-- 顶部：状态标签和操作按钮 -->
        <div class="flex justify-between items-start mb-4">
          <div class="flex items-center gap-3">
            <span
              :class="[
                'px-3 py-1 text-sm font-medium rounded-full',
                comment.status === 'approved'
                  ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
                  : 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400'
              ]"
            >
              {{ comment.status === 'approved' ? '已通过' : '待审核' }}
            </span>
            <span class="text-slate-400 text-sm">
              {{ formatDate(comment.created_at) }}
            </span>
          </div>
          <div class="flex gap-3">
            <button
              v-if="comment.status !== 'approved'"
              @click="approve(comment.id)"
              class="px-5 py-2 bg-green-500 hover:bg-green-600 text-white rounded-lg font-medium transition-colors"
            >
              通过审核
            </button>
            <button
              @click="handleDelete(comment.id)"
              class="px-5 py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg font-medium transition-colors"
            >
              删除
            </button>
          </div>
        </div>

        <!-- 评论内容 -->
        <div class="bg-slate-50 dark:bg-slate-800/50 rounded-lg p-4 mb-4">
          <p class="text-slate-700 dark:text-slate-200 leading-relaxed">{{ comment.content }}</p>
        </div>

        <!-- 底部：用户和文章信息 -->
        <div class="flex items-center justify-between text-sm">
          <div class="flex items-center gap-4">
            <div class="flex items-center gap-2">
              <div class="w-8 h-8 bg-gradient-to-br from-primary-400 to-primary-600 rounded-full flex items-center justify-center">
                <span class="text-white text-xs font-bold">
                  {{ (comment.user.nickname || comment.user.username).charAt(0).toUpperCase() }}
                </span>
              </div>
              <span class="font-medium text-slate-700 dark:text-slate-200">
                {{ comment.user.nickname || comment.user.username }}
              </span>
            </div>
            <span class="text-slate-400">{{ comment.user.email }}</span>
          </div>
          <router-link
            :to="`/post/${comment.post_id}`"
            class="text-primary-500 hover:text-primary-600 hover:underline"
            target="_blank"
          >
            📄 {{ comment.post_title || `文章 #${comment.post_id}` }}
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>
