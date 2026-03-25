<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { mediaApi } from '@/api'
import type { Media } from '@/types'

const mediaList = ref<Media[]>([])
const loading = ref(true)
const uploading = ref(false)

onMounted(async () => {
  await loadMedia()
})

async function loadMedia() {
  try {
    const { data } = await mediaApi.list()
    mediaList.value = data.items
  } finally {
    loading.value = false
  }
}

async function handleUpload(event: Event) {
  const file = (event.target as HTMLInputElement).files?.[0]
  if (!file) return

  uploading.value = true
  try {
    await mediaApi.upload(file)
    await loadMedia()
  } catch (e: any) {
    alert(e.response?.data?.detail || '上传失败')
  } finally {
    uploading.value = false
  }
}

async function handleDelete(id: number) {
  if (!confirm('确定删除该文件吗？')) return
  try {
    await mediaApi.delete(id)
    await loadMedia()
  } catch (e: any) {
    alert(e.response?.data?.detail || '删除失败')
  }
}

function formatSize(bytes: number) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / 1024 / 1024).toFixed(1) + ' MB'
}

function copyUrl(path: string) {
  navigator.clipboard.writeText(window.location.origin + path)
  alert('链接已复制')
}
</script>

<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold text-slate-800 dark:text-slate-100">媒体库</h1>
      <label
        class="px-5 py-2 bg-primary-500 hover:bg-primary-600 text-white rounded-lg font-medium transition-colors cursor-pointer"
        :class="{ 'opacity-50 cursor-wait': uploading }"
      >
        <span v-if="uploading">上传中...</span>
        <span v-else>上传文件</span>
        <input
          type="file"
          accept="image/*"
          class="hidden"
          @change="handleUpload"
          :disabled="uploading"
        />
      </label>
    </div>

    <div v-if="loading" class="flex justify-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-4 border-primary-500 border-t-transparent"></div>
    </div>

    <div v-else-if="mediaList.length === 0" class="card p-12 text-center text-slate-500">
      暂无文件，点击上方按钮上传
    </div>

    <div v-else class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
      <div
        v-for="media in mediaList"
        :key="media.id"
        class="card overflow-hidden group hover:shadow-lg transition-shadow"
      >
        <!-- 图片预览 -->
        <div class="aspect-square bg-slate-100 dark:bg-slate-700 relative">
          <img
            v-if="media.mimetype.startsWith('image')"
            :src="media.filepath"
            class="w-full h-full object-cover"
          />
          <div v-else class="w-full h-full flex items-center justify-center text-4xl">
            📄
          </div>
          <!-- 悬停操作层 -->
          <div class="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-3">
            <button
              @click="copyUrl(media.filepath)"
              class="px-4 py-2 bg-white hover:bg-slate-100 text-slate-800 rounded-lg font-medium transition-colors"
            >
              复制链接
            </button>
            <button
              @click="handleDelete(media.id)"
              class="px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg font-medium transition-colors"
            >
              删除
            </button>
          </div>
        </div>
        <!-- 文件信息 -->
        <div class="p-3">
          <p class="text-slate-800 dark:text-slate-200 text-sm font-medium truncate">{{ media.filename }}</p>
          <p class="text-slate-400 text-xs mt-1">{{ formatSize(media.filesize) }}</p>
        </div>
      </div>
    </div>
  </div>
</template>
