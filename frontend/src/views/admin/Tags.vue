<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { tagApi } from '@/api'
import type { Tag } from '@/types'

const tags = ref<Tag[]>([])
const loading = ref(true)
const newTag = ref('')

onMounted(async () => {
  await loadTags()
})

async function loadTags() {
  try {
    const { data } = await tagApi.list()
    tags.value = data
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

async function addTag() {
  if (!newTag.value.trim()) return
  try {
    await tagApi.create({ name: newTag.value.trim() })
    newTag.value = ''
    await loadTags()
  } catch (e: any) {
    alert(e.response?.data?.detail || '添加失败')
  }
}

async function handleDelete(id: number) {
  if (!confirm('确定删除该标签吗？')) return
  try {
    await tagApi.delete(id)
    await loadTags()
  } catch (e: any) {
    alert(e.response?.data?.detail || '删除失败')
  }
}
</script>

<template>
  <div>
    <h1 class="text-2xl font-bold text-slate-800 dark:text-slate-100 mb-6">标签管理</h1>

    <!-- 添加表单 -->
    <div class="card p-6 mb-6">
      <div class="flex gap-4">
        <input
          v-model="newTag"
          type="text"
          placeholder="输入标签名称"
          class="input flex-1"
          @keyup.enter="addTag"
        />
        <button
          @click="addTag"
          class="px-5 py-2 bg-primary-500 hover:bg-primary-600 text-white rounded-lg font-medium transition-colors"
        >
          添加标签
        </button>
      </div>
    </div>

    <!-- 加载中 -->
    <div v-if="loading" class="flex justify-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-4 border-primary-500 border-t-transparent"></div>
    </div>

    <!-- 标签列表 -->
    <div v-else class="space-y-4">
      <div
        v-for="tag in tags"
        :key="tag.id"
        class="card p-6 hover:shadow-md transition-shadow"
      >
        <div class="flex justify-between items-center">
          <div class="flex items-center gap-3">
            <span class="px-3 py-1 bg-primary-100 dark:bg-primary-900/30 text-primary-600 dark:text-primary-400 rounded-full font-medium">
              {{ tag.name }}
            </span>
            <span class="text-slate-400 text-sm">
              创建于 {{ new Date(tag.created_at).toLocaleDateString('zh-CN') }}
            </span>
          </div>
          <button
            @click="handleDelete(tag.id)"
            class="px-5 py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg font-medium transition-colors"
          >
            删除
          </button>
        </div>
      </div>

      <div v-if="tags.length === 0" class="text-center py-12 text-slate-500 dark:text-slate-400">
        暂无标签
      </div>
    </div>
  </div>
</template>
