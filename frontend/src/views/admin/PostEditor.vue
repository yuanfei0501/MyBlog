<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import { postApi, categoryApi, tagApi } from '@/api'
import type { Category, Tag } from '@/types'

const route = useRoute()
const router = useRouter()

const isEdit = computed(() => !!route.params.id)
const saving = ref(false)

// 表单数据
const title = ref('')
const content = ref('')

// 选项数据
const categories = ref<Category[]>([])
const allTags = ref<Tag[]>([])
const selectedTags = ref<string[]>([])

// 设置面板
const showSettings = ref(false)
const categoryId = ref<number | null>(null)
const coverImage = ref('')
const summary = ref('')
const status = ref('draft')
const isTop = ref(false)

// 预览
const renderedContent = computed(() => {
  if (!content.value) return ''
  return DOMPurify.sanitize(marked(content.value) as string)
})

// 字数统计
const wordCount = computed(() => {
  return content.value.replace(/\s/g, '').length
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
  try {
    const { data: post } = await postApi.getById(Number(route.params.id))
    title.value = post.title
    content.value = post.content
    summary.value = post.summary || ''
    coverImage.value = post.cover_image || ''
    categoryId.value = post.category?.id || null
    selectedTags.value = post.tags?.map((t: Tag) => t.name) || []
    status.value = post.status
    isTop.value = post.is_top
  } catch (e) {
    console.error(e)
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

// 快捷键
function handleKeydown(e: KeyboardEvent) {
  if ((e.metaKey || e.ctrlKey) && e.key === 's') {
    e.preventDefault()
    handleSave(false)
  }
}
</script>

<template>
  <!-- 全屏编辑器，覆盖整个页面 -->
  <div
    class="fixed inset-0 z-50 flex flex-col bg-white dark:bg-slate-900"
    @keydown="handleKeydown"
  >
    <!-- 顶部工具栏 -->
    <div class="h-14 border-b border-slate-200 dark:border-slate-700 flex items-center justify-between px-6 shrink-0 bg-white dark:bg-slate-900">
      <div class="flex items-center gap-4">
        <button
          @click="router.push('/admin/posts')"
          class="p-2 rounded-lg text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
        </button>
        <input
          v-model="title"
          type="text"
          placeholder="请输入文章标题..."
          class="text-xl font-bold bg-transparent border-none outline-none text-slate-800 dark:text-slate-100 placeholder-slate-400 w-80"
        />
        <span class="text-slate-400 text-sm">{{ wordCount }} 字</span>
      </div>
      <div class="flex items-center gap-3">
        <button
          @click="showSettings = !showSettings"
          :class="[
            'px-4 py-2 rounded-lg font-medium transition-colors',
            showSettings
              ? 'bg-primary-500 text-white'
              : 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600'
          ]"
        >
          {{ showSettings ? '隐藏设置' : '设置' }}
        </button>
        <button
          @click="handleSave(false)"
          :disabled="saving"
          class="px-4 py-2 bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600 rounded-lg font-medium transition-colors disabled:opacity-50"
        >
          保存草稿
        </button>
        <button
          @click="handleSave(true)"
          :disabled="saving"
          class="px-6 py-2 bg-primary-500 hover:bg-primary-600 text-white rounded-lg font-medium transition-colors disabled:opacity-50"
        >
          发布
        </button>
      </div>
    </div>

    <!-- 主内容区 -->
    <div class="flex-1 flex overflow-hidden">
      <!-- 编辑区 -->
      <div class="flex-1 flex flex-col border-r border-slate-200 dark:border-slate-700 min-w-0">
        <textarea
          v-model="content"
          placeholder="开始写作吧... 支持 Markdown 格式&#10;&#10;快捷键: Ctrl/Cmd + S 保存草稿"
          class="flex-1 w-full p-8 resize-none outline-none bg-transparent text-slate-800 dark:text-slate-200 text-base leading-relaxed"
        ></textarea>
      </div>

      <!-- 预览区 -->
      <div class="flex-1 overflow-auto bg-slate-50 dark:bg-slate-800/50 border-r border-slate-200 dark:border-slate-700 min-w-0">
        <article
          v-if="content"
          class="prose prose-slate dark:prose-invert max-w-3xl mx-auto p-8"
          v-html="renderedContent"
        ></article>
        <div v-else class="flex items-center justify-center h-full text-slate-400">
          <div class="text-center">
            <svg class="w-16 h-16 mx-auto mb-4 text-slate-300 dark:text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
            </svg>
            <p class="text-lg">预览区域</p>
            <p class="text-sm mt-1">在左侧输入内容后，这里会实时显示渲染效果</p>
          </div>
        </div>
      </div>

      <!-- 右侧设置面板 -->
      <Transition
        enter-active-class="transition-all duration-300"
        enter-from-class="translate-x-full opacity-0"
        leave-active-class="transition-all duration-300"
        leave-to-class="translate-x-full opacity-0"
      >
        <div
          v-if="showSettings"
          class="w-80 border-l border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 overflow-auto shrink-0"
        >
          <div class="p-6 space-y-6">
            <!-- 分类 -->
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">分类</label>
              <select v-model="categoryId" class="input w-full">
                <option :value="null">无分类</option>
                <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
              </select>
            </div>

            <!-- 标签 -->
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">标签</label>
              <div class="flex flex-wrap gap-2 mb-3">
                <span
                  v-for="tag in selectedTags"
                  :key="tag"
                  class="px-3 py-1 bg-primary-100 dark:bg-primary-900/30 text-primary-600 dark:text-primary-400 text-sm rounded-full flex items-center gap-1"
                >
                  {{ tag }}
                  <button @click="selectedTags = selectedTags.filter(t => t !== tag)" class="hover:text-red-500 ml-1">×</button>
                </span>
              </div>
              <div class="flex gap-2">
                <input v-model="newTag" type="text" placeholder="添加标签" class="input flex-1" @keyup.enter="addTag" />
                <button @click="addTag" class="px-3 py-2 bg-primary-500 hover:bg-primary-600 text-white rounded-lg text-sm font-medium">+</button>
              </div>
              <div class="mt-3 flex flex-wrap gap-1">
                <button
                  v-for="tag in allTags.filter(t => !selectedTags.includes(t.name))"
                  :key="tag.id"
                  @click="selectedTags.push(tag.name)"
                  class="text-xs px-2 py-1 bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 rounded hover:bg-primary-100 dark:hover:bg-primary-900/30 transition-colors"
                >
                  + {{ tag.name }}
                </button>
              </div>
            </div>

            <!-- 封面图 -->
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">封面图</label>
              <input v-model="coverImage" type="text" placeholder="图片 URL" class="input w-full" />
              <div v-if="coverImage" class="mt-2 aspect-video bg-slate-100 dark:bg-slate-700 rounded-lg overflow-hidden">
                <img :src="coverImage" class="w-full h-full object-cover" />
              </div>
            </div>

            <!-- 摘要 -->
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">摘要</label>
              <textarea v-model="summary" placeholder="文章摘要（可选，不填则自动截取）" class="input w-full h-24 resize-none"></textarea>
            </div>

            <!-- 其他设置 -->
            <div class="space-y-4 pt-4 border-t border-slate-200 dark:border-slate-700">
              <div class="flex items-center justify-between">
                <span class="text-sm text-slate-600 dark:text-slate-300">置顶文章</span>
                <button
                  @click="isTop = !isTop"
                  :class="[
                    'w-10 h-6 rounded-full transition-colors relative',
                    isTop ? 'bg-primary-500' : 'bg-slate-300 dark:bg-slate-600'
                  ]"
                >
                  <span
                    :class="[
                      'absolute top-1 w-4 h-4 bg-white rounded-full transition-all',
                      isTop ? 'left-5' : 'left-1'
                    ]"
                  ></span>
                </button>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-sm text-slate-600 dark:text-slate-300">发布状态</span>
                <select v-model="status" class="input w-auto text-sm py-1 px-3">
                  <option value="draft">草稿</option>
                  <option value="published">已发布</option>
                </select>
              </div>
            </div>
          </div>
        </div>
      </Transition>
    </div>
  </div>
</template>

<style scoped>
.prose :deep(h1),
.prose :deep(h2),
.prose :deep(h3),
.prose :deep(h4) {
  @apply text-slate-800 dark:text-slate-100 font-bold;
}
.prose :deep(p) {
  @apply text-slate-600 dark:text-slate-300 leading-relaxed;
}
.prose :deep(a) {
  @apply text-primary-500 hover:underline;
}
.prose :deep(code) {
  @apply text-primary-500 bg-slate-100 dark:bg-slate-700 px-1.5 py-0.5 rounded text-sm;
}
.prose :deep(pre) {
  @apply bg-slate-800 dark:bg-slate-900 rounded-lg p-4 overflow-x-auto;
}
.prose :deep(pre code) {
  @apply bg-transparent p-0 text-slate-200;
}
.prose :deep(blockquote) {
  @apply border-l-4 border-primary-500 pl-4 italic text-slate-500;
}
.prose :deep(ul),
.prose :deep(ol) {
  @apply pl-6;
}
.prose :deep(ul) {
  @apply list-disc;
}
.prose :deep(ol) {
  @apply list-decimal;
}
.prose :deep(img) {
  @apply rounded-lg max-w-full;
}
.prose :deep(table) {
  @apply w-full border-collapse;
}
.prose :deep(th),
.prose :deep(td) {
  @apply border border-slate-200 dark:border-slate-700 px-4 py-2;
}
.prose :deep(th) {
  @apply bg-slate-100 dark:bg-slate-800 font-medium;
}
</style>
