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
        <div class="flex gap-2">
          <button @click="handleSave" class="btn-primary flex-1">
            {{ editing ? '更新' : '添加' }}
          </button>
          <button v-if="editing" @click="cancelEdit" class="btn-secondary">取消</button>
        </div>
      </div>
    </div>

    <!-- 列表 -->
    <div v-if="loading" class="flex justify-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-4 border-primary-500 border-t-transparent"></div>
    </div>

    <div v-else class="card overflow-hidden">
      <table class="w-full">
        <thead class="bg-slate-50 dark:bg-slate-700">
          <tr>
            <th class="px-6 py-3 text-left text-sm font-medium text-slate-500 dark:text-slate-300">名称</th>
            <th class="px-6 py-3 text-left text-sm font-medium text-slate-500 dark:text-slate-300">描述</th>
            <th class="px-6 py-3 text-right text-sm font-medium text-slate-500 dark:text-slate-300">操作</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100 dark:divide-slate-700">
          <tr v-for="cat in categories" :key="cat.id" class="hover:bg-slate-50 dark:hover:bg-slate-700/50">
            <td class="px-6 py-4 text-slate-800 dark:text-slate-200">{{ cat.name }}</td>
            <td class="px-6 py-4 text-slate-500 dark:text-slate-400">{{ cat.description || '-' }}</td>
            <td class="px-6 py-4 text-right">
              <button @click="startEdit(cat)" class="text-primary-500 hover:text-primary-600 mr-3">编辑</button>
              <button @click="handleDelete(cat.id)" class="text-red-500 hover:text-red-600">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
