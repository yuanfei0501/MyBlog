<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import hljs from 'highlight.js'
import 'highlight.js/styles/github-dark.css'
import { postApi, commentApi } from '@/api'
import { useUserStore } from '@/stores/user'
import type { Post, Comment } from '@/types'

const route = useRoute()
const userStore = useUserStore()

const post = ref<Post | null>(null)
const comments = ref<Comment[]>([])
const loading = ref(true)
const commentContent = ref('')
const replyTo = ref<number | null>(null)

// 配置 marked
marked.setOptions({
  highlight: (code, lang) => {
    if (lang && hljs.getLanguage(lang)) {
      return hljs.highlight(code, { language: lang }).value
    }
    return hljs.highlightAuto(code).value
  },
  breaks: true,
  gfm: true,
})

const renderedContent = computed(() => {
  if (!post.value) return ''
  return DOMPurify.sanitize(marked(post.value.content) as string)
})

onMounted(async () => {
  await loadPost()
  await loadComments()
})

async function loadPost() {
  try {
    const { data } = await postApi.get(route.params.slug as string)
    post.value = data
  } catch {
    // 处理错误
  } finally {
    loading.value = false
  }
}

async function loadComments() {
  if (!post.value) return
  try {
    const { data } = await commentApi.listByPost(post.value.id)
    comments.value = data
  } catch (e) {
    console.error(e)
  }
}

async function submitComment() {
  if (!commentContent.value.trim() || !post.value) return

  try {
    await commentApi.create({
      content: commentContent.value,
      post_id: post.value.id,
      parent_id: replyTo.value || undefined,
    })
    commentContent.value = ''
    replyTo.value = null
    await loadComments()
  } catch (e) {
    console.error(e)
  }
}

function setReply(commentId: number) {
  replyTo.value = commentId
}

function cancelReply() {
  replyTo.value = null
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
  <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
    <!-- 加载中 -->
    <div v-if="loading" class="flex justify-center py-20">
      <div class="animate-spin rounded-full h-12 w-12 border-4 border-primary-500 border-t-transparent"></div>
    </div>

    <template v-else-if="post">
      <!-- 文章头部 -->
      <header class="mb-12">
        <!-- 分类 -->
        <div v-if="post.category" class="mb-4">
          <router-link
            :to="`/category/${post.category.slug}`"
            class="text-primary-500 font-medium hover:text-primary-600"
          >
            {{ post.category.name }}
          </router-link>
        </div>

        <!-- 标题 -->
        <h1 class="text-3xl md:text-4xl font-bold text-slate-900 dark:text-slate-100 mb-6">
          {{ post.title }}
        </h1>

        <!-- 元信息 -->
        <div class="flex flex-wrap items-center gap-4 text-slate-500 dark:text-slate-400">
          <div class="flex items-center space-x-2">
            <div class="w-8 h-8 bg-gradient-to-br from-primary-400 to-violet-400 rounded-full flex items-center justify-center">
              <span class="text-white text-sm">
                {{ post.author.nickname?.[0] || post.author.username[0] }}
              </span>
            </div>
            <span>{{ post.author.nickname || post.author.username }}</span>
          </div>
          <span>·</span>
          <span>{{ formatDate(post.created_at) }}</span>
          <span>·</span>
          <span class="flex items-center space-x-1">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
            <span>{{ post.view_count }} 阅读</span>
          </span>
        </div>

        <!-- 标签 -->
        <div class="flex flex-wrap gap-2 mt-6">
          <router-link
            v-for="tag in post.tags"
            :key="tag.id"
            :to="`/tag/${tag.slug}`"
            class="px-3 py-1 bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 text-sm rounded-full hover:bg-primary-100 dark:hover:bg-primary-900/30 hover:text-primary-500 transition-colors"
          >
            #{{ tag.name }}
          </router-link>
        </div>
      </header>

      <!-- 封面图 -->
      <div v-if="post.cover_image" class="mb-12 rounded-2xl overflow-hidden">
        <img
          :src="post.cover_image"
          :alt="post.title"
          class="w-full h-auto"
        />
      </div>

      <!-- 文章内容 -->
      <article class="prose-custom" v-html="renderedContent"></article>

      <!-- 评论区 -->
      <section class="mt-16 pt-8 border-t border-slate-200 dark:border-slate-700">
        <h2 class="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-8">
          评论 ({{ comments.length }})
        </h2>

        <!-- 发表评论 -->
        <div v-if="userStore.isLoggedIn" class="mb-8">
          <div class="text-sm text-slate-500 mb-2" v-if="replyTo">
            回复评论...
            <button @click="cancelReply" class="text-primary-500 ml-2">取消</button>
          </div>
          <textarea
            v-model="commentContent"
            placeholder="写下你的评论..."
            class="input min-h-[120px] resize-none"
          ></textarea>
          <div class="flex justify-end mt-3">
            <button
              @click="submitComment"
              :disabled="!commentContent.trim()"
              class="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
            >
              发表评论
            </button>
          </div>
        </div>
        <div v-else class="mb-8 p-6 bg-slate-50 dark:bg-slate-800 rounded-lg text-center">
          <p class="text-slate-500 dark:text-slate-400">
            <router-link to="/login" class="text-primary-500 hover:text-primary-600">登录</router-link>
            后参与评论
          </p>
        </div>

        <!-- 评论列表 -->
        <div class="space-y-6">
          <div
            v-for="comment in comments"
            :key="comment.id"
            class="p-4 bg-white dark:bg-slate-800 rounded-lg border border-slate-100 dark:border-slate-700"
          >
            <div class="flex items-start space-x-3">
              <div class="w-10 h-10 bg-gradient-to-br from-primary-400 to-violet-400 rounded-full flex items-center justify-center flex-shrink-0">
                <span class="text-white">
                  {{ comment.user.nickname?.[0] || comment.user.username[0] }}
                </span>
              </div>
              <div class="flex-1">
                <div class="flex items-center space-x-2 mb-2">
                  <span class="font-medium text-slate-800 dark:text-slate-200">
                    {{ comment.user.nickname || comment.user.username }}
                  </span>
                  <span class="text-slate-400 text-sm">{{ formatDate(comment.created_at) }}</span>
                </div>
                <p class="text-slate-600 dark:text-slate-300">{{ comment.content }}</p>
                <button
                  v-if="userStore.isLoggedIn"
                  @click="setReply(comment.id)"
                  class="text-sm text-primary-500 mt-2 hover:text-primary-600"
                >
                  回复
                </button>
              </div>
            </div>

            <!-- 子评论 -->
            <div v-if="comment.replies?.length" class="mt-4 ml-12 space-y-4">
              <div
                v-for="reply in comment.replies"
                :key="reply.id"
                class="p-3 bg-slate-50 dark:bg-slate-700/50 rounded-lg"
              >
                <div class="flex items-center space-x-2 mb-1">
                  <span class="font-medium text-slate-700 dark:text-slate-300 text-sm">
                    {{ reply.user.nickname || reply.user.username }}
                  </span>
                  <span class="text-slate-400 text-xs">{{ formatDate(reply.created_at) }}</span>
                </div>
                <p class="text-slate-600 dark:text-slate-400 text-sm">{{ reply.content }}</p>
              </div>
            </div>
          </div>
        </div>
      </section>
    </template>

    <!-- 文章不存在 -->
    <div v-else class="text-center py-20">
      <p class="text-slate-500 dark:text-slate-400">文章不存在或已被删除</p>
      <router-link to="/" class="text-primary-500 hover:text-primary-600 mt-4 inline-block">
        返回首页
      </router-link>
    </div>
  </div>
</template>
