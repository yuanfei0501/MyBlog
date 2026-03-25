<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { categoryApi } from '@/api'
import type { Category } from '@/types'

const categories = ref<Category[]>([])
const loading = ref(true)
const editing = ref<number | null>(null)
const form = ref({ name: '', description: '' })

onMounted(async () => {
  await loadCategories()
})

async function loadCategories() {
  try {
    const { data } = await categoryApi.list()
    categories.value = data
  } finally {
    loading.value = false
  }
}

async function handleSave() {
  if (!form.value.name.trim()) return

  try {
    if (editing.value) {
      await categoryApi.update(editing.value, form.value)
    } else {
      await categoryApi.create(form.value)
    }
    form.value = { name: '', description: '' }
    editing.value = null
    await loadCategories()
  } catch (e: any) {
    alert(e.response?.data?.detail || '操作失败')
  }
}

function startEdit(cat: Category) {
  editing.value = cat.id
  form.value = { name: cat.name, description: cat.description || '' }
}

function cancelEdit() {
  editing.value = null
  form.value = { name: '', description: '' }
}

async function handleDelete(id: number) {
  if (!confirm('确定删除该分类吗？')) return
  try {
    await categoryApi.delete(id)
    await loadCategories()
  } catch (e: any) {
    alert(e.response?.data?.detail || '删除失败')
  }
}
</script>

<template>
  <div>
    <h1 class="text-2xl font-bold text-slate-800 dark:text-slate-100 mb-6">分类管理</h1>

    <!-- 添加/编辑表单 -->
    <div class="card p-6 mb-6">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <input v-model="form.name" type="text" placeholder="分类名称" class="input" />
        <input v-model="form.description" type="text" placeholder="描述（可选）" class="input" />
        <div class="flex gap-3">
          <button
            @click="handleSave"
            class="flex-1 px-5 py-2 bg-primary-500 hover:bg-primary-600 text-white rounded-lg font-medium transition-colors"
          >
            {{ editing ? '更新' : '添加' }}
          </button>
          <button
            v-if="editing"
            @click="cancelEdit"
            class="px-5 py-2 bg-slate-200 dark:bg-slate-600 hover:bg-slate-300 dark:hover:bg-slate-500 text-slate-700 dark:text-slate-200 rounded-lg font-medium transition-colors"
          >
            取消
          </button>
        </div>
      </div>
    </div>

    <!-- 列表 -->
    <div v-if="loading" class="flex justify-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-4 border-primary-500 border-t-transparent"></div>
    </div>

    <div v-else class="space-y-4">
      <div
        v-for="cat in categories"
        :key="cat.id"
        class="card p-6 hover:shadow-md transition-shadow"
      >
        <div class="flex justify-between items-center">
          <div>
            <h3 class="font-bold text-lg text-slate-800 dark:text-slate-100">{{ cat.name }}</h3>
            <p class="text-slate-500 dark:text-slate-400 text-sm mt-1">{{ cat.description || '暂无描述' }}</p>
          </div>
          <div class="flex gap-3">
            <button
              @click="startEdit(cat)"
              class="px-5 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg font-medium transition-colors"
            >
              编辑
            </button>
            <button
              @click="handleDelete(cat.id)"
              class="px-5 py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg font-medium transition-colors"
            >
              删除
            </button>
          </div>
        </div>
      </div>

      <div v-if="categories.length === 0" class="text-center py-12 text-slate-500 dark:text-slate-400">
        暂无分类
      </div>
    </div>
  </div>
</template>
