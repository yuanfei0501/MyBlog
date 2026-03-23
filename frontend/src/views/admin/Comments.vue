<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { commentApi } from '@/api'
import type { Comment } from '@/types'

const comments = ref<Comment[]>([])
const loading = ref(true)

onMounted(async () => {
  await loadComments()
})

async function loadComments() {
  try {
    // 这里简化处理，实际应该有专门的管理 API
    comments.value = []
  } finally {
    loading.value = false
  }
}

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
  return new Date(date).toLocaleDateString('zh-CN')
}
</script>

<template>
  <div>
    <h1 class="text-2xl font-bold text-slate-800 dark:text-slate-100 mb-6">评论管理</h1>

    <div v-if="loading" class="flex justify-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-4 border-primary-500 border-t-transparent"></div>
    </div>

    <div v-else-if="comments.length === 0" class="card p-12 text-center text-slate-500">
      暂无评论
    </div>

    <div v-else class="space-y-4">
      <div v-for="comment in comments" :key="comment.id" class="card p-4">
        <div class="flex justify-between items-start">
          <div class="flex-1">
            <div class="flex items-center gap-2 mb-2">
              <span class="font-medium text-slate-800 dark:text-slate-100">
                {{ comment.user.nickname || comment.user.username }}
              </span>
              <span
                :class="[
                  'px-2 py-0.5 text-xs rounded',
                  comment.status === 'approved'
                    ? 'bg-green-100 text-green-600'
                    : 'bg-yellow-100 text-yellow-600'
                ]"
              >
                {{ comment.status === 'approved' ? '已通过' : '待审核' }}
              </span>
            </div>
            <p class="text-slate-600 dark:text-slate-300">{{ comment.content }}</p>
            <p class="text-slate-400 text-sm mt-2">{{ formatDate(comment.created_at) }}</p>
          </div>
          <div class="flex gap-2">
            <button
              v-if="comment.status !== 'approved'"
              @click="approve(comment.id)"
              class="text-green-500 hover:text-green-600 text-sm"
            >
              通过
            </button>
            <button @click="handleDelete(comment.id)" class="text-red-500 hover:text-red-600 text-sm">
              删除
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
