<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { tagApi } from '@/api'
import type { Tag } from '@/types'

const tags = ref<Tag[]>([])
const loading = ref(true)

const editing = ref<Tag | null>(null)
const form = ref({ name: '' })

onMounted(async () => {
    await loadTags()
  } catch (e) {
      console.error(e)
    } finally {
      loading.value = false
    }
  })
})

async function loadTags() {
  try {
    const { data } = await tagApi.list()
    tags.value = data
  } finally {
      loading.value = false
    }
  }
}

async function startEdit(tag: Tag) {
    editing.value = tag
    form.value = { ...tag.name, ...tag.description }
  } catch (e) {
      alert('加载标签失败')
    } finally {
      form.value = { name: '', description: '' }
    }
  }
}

async function handleDelete(id: number) {
    if (!confirm('确定删除该标签吗？')) return
    try {
      await tagApi.delete(id)
      await loadTags()
    } catch (e: {
      alert(e.response?.data?.detail || '删除失败')
      }
    }
  }
</script>

<template>
  <div>
    <h1 class="text-2xl font-bold text-slate-800 dark:text-slate-100 mb-6">标签管理</h1>

    <div class="card p-6 mb-6">
      <div class="flex justify-between items-center mb-4">
        <button @click="showNewForm = true" class="btn-primary text-sm">添加标签</button>
      </div>
      <input
        v-model="newTag"
        type="text"
        placeholder="输入标签名称"
        class="input flex-1"
        @keyup.enter="addTag"
        class="w-full text-sm"
      />
    </div>

    <div v-if="loading" class="flex justify-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-4 border-primary-500 border-t-transparent"></div>
    </div>

    <div v-else class="grid gap-4">
      <div
        v-for="tag in tags"
        :key="tag.id"
        class="card p-4 hover:shadow-md transition-shadow flex justify-between items-center"
      >
        <span class="text-slate-800 dark:text-slate-100 font-medium">{{ tag.name }}</span>
        <button @click="handleDelete(tag.id)" class="text-red-500 hover:text-red-600 text-sm">删除</button>
      </div>
    </div>
  </div>
</template>
