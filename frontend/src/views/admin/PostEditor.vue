<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import { postApi, categoryApi, tagApi } from '@/api'
import { useUserStore } from '@/stores/user'
import type { Category, Tag } from '@/types'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const isEdit = computed(() => !!route.params.id)
const loading = ref(false)
const saving = ref(false)

// 表单数据
const title = ref('')
const content = ref('')
const summary = ref('')
const coverImage = ref('')
const categoryId = ref<number | null>(null)
const selectedTags = ref<string[]>([])
const status = ref('draft')
const isTop = ref(false)

// 选项数据
const categories = ref<Category[]>([])
const allTags = ref<Tag[]>([])

// 预览
const showPreview = ref(false)
const renderedContent = computed(() => {
  if (!content.value) return ''
  return DOMPurify.sanitize(marked(content.value) as string)
})

onMounted(async () => {
  await Promise.all([loadCategories(), loadTags()])
  if (isEdit.value) {
    await loadPost()
  }
})

async function loadCategories() {
  try {
    const { data } = await categoryApi.list()
    categories.value = data
  } catch (e) {
    console.error(e)
  }
}

async function loadTags() {
  try {
    const { data } = await tagApi.list()
    allTags.value = data
  } catch (e) {
    console.error(e)
  }
}

async function loadPost() {
  loading.value = true
  try {
    // 通过列表 API 获取文章（简化处理）
    const { data } = await postApi.list({ page: 1, page_size: 1000, status: '' })
    const post = data.items.find((p: any) => p.id === Number(route.params.id))
    if (post) {
      title.value = post.title
      content.value = post.content
      summary.value = post.summary || ''
      coverImage.value = post.cover_image || ''
      categoryId.value = post.category?.id || null
      selectedTags.value = post.tags.map((t: Tag) => t.name)
      status.value = post.status
      isTop.value = post.is_top
    }
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

async function handleSave(publish = false) {
  if (!title.value.trim() || !content.value.trim()) {
    alert('请填写标题和内容')
    return
  }

  saving.value = true
  try {
    const data = {
      title: title.value,
      content: content.value,
      summary: summary.value || undefined,
      cover_image: coverImage.value || undefined,
      category_id: categoryId.value || undefined,
      tags: selectedTags.value,
      status: publish ? 'published' : status.value,
      is_top: isTop.value,
    }

    if (isEdit.value) {
      await postApi.update(Number(route.params.id), data)
    } else {
      await postApi.create(data)
    }

    router.push('/admin/posts')
  } catch (e: any) {
    alert(e.response?.data?.detail || '保存失败')
  } finally {
    saving.value = false
  }
}

// 添加标签
const newTag = ref('')
function addTag() {
  if (newTag.value.trim() && !selectedTags.value.includes(newTag.value.trim())) {
    selectedTags.value.push(newTag.value.trim())
    newTag.value = ''
  }
}
</script>

<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold text-slate-800 dark:text-slate-100">
        {{ isEdit ? '编辑文章' : '写文章' }}
      </h1>
      <div class="flex gap-3">
        <button @click="showPreview = !showPreview" class="btn-secondary">
          {{ showPreview ? '隐藏预览' : '预览' }}
        </button>
        <button @click="handleSave(false)" :disabled="saving" class="btn-secondary">
          保存草稿
        </button>
        <button @click="handleSave(true)" :disabled="saving" class="btn-primary">
          发布
        </button>
      </div>
    </div>

    <div v-if="loading" class="flex justify-center py-20">
      <div class="animate-spin rounded-full h-12 w-12 border-4 border-primary-500 border-t-transparent"></div>
    </div>

    <div v-else class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- 编辑区 -->
      <div class="lg:col-span-2 space-y-6">
        <!-- 标题 -->
        <div>
          <input
            v-model="title"
            type="text"
            placeholder="文章标题"
            class="input text-xl font-bold"
          />
        </div>

        <!-- 内容编辑/预览 -->
        <div class="grid grid-cols-1 gap-4" :class="{ 'lg:grid-cols-2': showPreview }">
          <div>
            <textarea
              v-model="content"
              placeholder="支持 Markdown 格式..."
              class="input min-h-[500px] font-mono resize-none"
            ></textarea>
          </div>
          <div v-if="showPreview" class="hidden lg:block">
            <div class="card p-6 min-h-[500px] overflow-auto">
              <article class="prose-custom" v-html="renderedContent"></article>
            </div>
          </div>
        </div>

        <!-- 摘要 -->
        <div>
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">摘要</label>
          <textarea
            v-model="summary"
            placeholder="文章摘要（可选）"
            class="input min-h-[100px] resize-none"
          ></textarea>
        </div>
      </div>

      <!-- 设置区 -->
      <div class="space-y-6">
        <!-- 分类 -->
        <div class="card p-4">
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">分类</label>
          <select v-model="categoryId" class="input">
            <option :value="null">无分类</option>
            <option v-for="cat in categories" :key="cat.id" :value="cat.id">
              {{ cat.name }}
            </option>
          </select>
        </div>

        <!-- 标签 -->
        <div class="card p-4">
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">标签</label>
          <div class="flex flex-wrap gap-2 mb-3">
            <span
              v-for="tag in selectedTags"
              :key="tag"
              class="px-2 py-1 bg-primary-100 dark:bg-primary-900/30 text-primary-600 dark:text-primary-400 text-sm rounded flex items-center gap-1"
            >
              {{ tag }}
              <button @click="selectedTags = selectedTags.filter(t => t !== tag)" class="hover:text-red-500">×</button>
            </span>
          </div>
          <div class="flex gap-2">
            <input
              v-model="newTag"
              type="text"
              placeholder="添加标签"
              class="input flex-1"
              @keyup.enter="addTag"
            />
            <button @click="addTag" class="btn-secondary text-sm">添加</button>
          </div>
          <div class="mt-3 flex flex-wrap gap-1">
            <button
              v-for="tag in allTags"
              :key="tag.id"
              @click="!selectedTags.includes(tag.name) && selectedTags.push(tag.name)"
              :class="[
                'text-xs px-2 py-1 rounded',
                selectedTags.includes(tag.name)
                  ? 'bg-slate-100 dark:bg-slate-700 text-slate-400'
                  : 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 hover:bg-primary-100 dark:hover:bg-primary-900/30'
              ]"
            >
              {{ tag.name }}
            </button>
          </div>
        </div>

        <!-- 封面图 -->
        <div class="card p-4">
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">封面图</label>
          <input
            v-model="coverImage"
            type="text"
            placeholder="图片 URL"
            class="input"
          />
        </div>

        <!-- 其他设置 -->
        <div class="card p-4 space-y-3">
          <div class="flex items-center justify-between">
            <span class="text-sm text-slate-600 dark:text-slate-300">置顶文章</span>
            <button
              @click="isTop = !isTop"
              :class="[
                'w-10 h-6 rounded-full transition-colors',
                isTop ? 'bg-primary-500' : 'bg-slate-300 dark:bg-slate-600'
              ]"
            >
              <span
                :class="[
                  'block w-4 h-4 bg-white rounded-full transition-transform',
                  isTop ? 'translate-x-5' : 'translate-x-1'
                ]"
              ></span>
            </button>
          </div>
          <div class="flex items-center justify-between">
            <span class="text-sm text-slate-600 dark:text-slate-300">状态</span>
            <select v-model="status" class="input w-auto text-sm">
              <option value="draft">草稿</option>
              <option value="published">已发布</option>
            </select>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
