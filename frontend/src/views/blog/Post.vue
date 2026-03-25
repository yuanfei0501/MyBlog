<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed, watch, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import hljs from 'highlight.js'
import 'highlight.js/styles/github-dark.css'
import { postApi, commentApi, followApi } from '@/api'
import { useRouter } from 'vue-router'

const router = useRouter()
import { useUserStore } from '@/stores/user'
import type { Post, Comment } from '@/types'

const route = useRoute()
const userStore = useUserStore()

const post = ref<Post | null>(null)
const comments = ref<Comment[]>([])
const loading = ref(true)
const commentContent = ref('')
const replyTo = ref<number | null>(null)

// 关注相关
const isFollowing = ref(false)
const followLoading = ref(false)
const followersCount = ref(0)
const postsCount = ref(0)
const showFollowersList = ref(false)
const followersList = ref<any[]>([])

// 目录相关
interface TocItem {
  id: string
  text: string
  level: number
}
const tocItems = ref<TocItem[]>([])
const activeTocId = ref('')

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

// 从内容中提取目录
function extractToc(html: string) {
  const parser = new DOMParser()
  const doc = parser.parseFromString(html, 'text/html')
  const headings = doc.querySelectorAll('h1, h2, h3, h4')
  const items: TocItem[] = []

  headings.forEach((heading, index) => {
    const level = parseInt(heading.tagName.charAt(1))
    const text = heading.textContent || ''
    const id = `heading-${index}`
    heading.id = id
    items.push({ id, text, level })
  })

  return {
    html: doc.body.innerHTML,
    toc: items
  }
}

// 处理后的内容
const processedContent = computed(() => {
  if (!renderedContent.value) return ''
  const { html, toc } = extractToc(renderedContent.value)
  tocItems.value = toc
  return html
})

// 滚动监听
let observer: IntersectionObserver | null = null

function setupScrollObserver() {
  if (observer) observer.disconnect()

  observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          activeTocId.value = entry.target.id
        }
      })
    },
    {
      rootMargin: '-80px 0px -80% 0px',
      threshold: 0
    }
  )

  nextTick(() => {
    tocItems.value.forEach((item) => {
      const el = document.getElementById(item.id)
      if (el && observer) {
        observer.observe(el)
      }
    })
  })
}

// 点击目录跳转
function scrollToHeading(id: string) {
  const el = document.getElementById(id)
  if (el) {
    const offset = 80
    const top = el.getBoundingClientRect().top + window.pageYOffset - offset
    window.scrollTo({ top, behavior: 'smooth' })
    activeTocId.value = id
  }
}

onMounted(async () => {
  await loadPost()
  await loadComments()
  if (tocItems.value.length > 0) {
    setupScrollObserver()
  }
})

onUnmounted(() => {
  if (observer) observer.disconnect()
})

watch(processedContent, () => {
  nextTick(() => {
    if (tocItems.value.length > 0) {
      setupScrollObserver()
    }
  })
})

async function loadPost() {
  try {
    const { data } = await postApi.get(route.params.slug as string)
    post.value = data
    // 加载关注状态
    if (userStore.isLoggedIn && post.value) {
      await loadFollowStatus()
      await loadFollowCount()
    }
  } catch {
    // 处理错误
  } finally {
    loading.value = false
  }
}

async function loadFollowStatus() {
  if (!post.value) return
  try {
    const { data } = await followApi.getStatus(post.value.author.id)
    isFollowing.value = data.is_following
  } catch {
    // 忽略错误
  }
}

async function loadFollowCount() {
  if (!post.value) return
  try {
    const { data } = await followApi.getStats(post.value.author.id)
    followersCount.value = data.followers
    postsCount.value = data.posts
  } catch {
    // 忽略错误
  }
}

async function toggleFollow() {
  if (!post.value || !userStore.isLoggedIn) {
    return
  }
  followLoading.value = true
  try {
    if (isFollowing.value) {
      await followApi.unfollow(post.value.author.id)
      isFollowing.value = false
      followersCount.value--
    } else {
      await followApi.follow(post.value.author.id)
      isFollowing.value = true
      followersCount.value++
    }
  } catch (e: any) {
    alert(e.response?.data?.detail || '操作失败')
  } finally {
    followLoading.value = false
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
  <div class="post-page">
    <!-- 加载中 -->
    <div v-if="loading" class="loading-wrapper">
      <div class="loading-spinner"></div>
    </div>

    <template v-else-if="post">
      <!-- 三栏布局 -->
      <div class="post-container">
        <!-- 左侧：作者信息 -->
        <aside class="left-sidebar">
          <div class="sticky-wrapper">
            <div class="author-card">
              <div class="author-avatar">
                <span>{{ post.author.nickname?.[0] || post.author.username[0] }}</span>
              </div>
              <h3 class="author-name">{{ post.author.nickname || post.author.username }}</h3>
              <p class="author-bio">{{ post.author.bio || '这个人很懒' }}</p>

              <div class="author-stats">
                <div class="stat-item clickable" @click="goToUserPosts">
                  <div class="stat-num">{{ postsCount }}</div>
                  <div class="stat-label">文章</div>
                </div>
                <div class="stat-item clickable" @click="showFollowers">
                  <div class="stat-num">{{ followersCount }}</div>
                  <div class="stat-label">粉丝</div>
                </div>
              </div>

              <!-- 粉丝列表弹窗 -->
              <div v-if="showFollowersList" class="followers-modal" @click.self="showFollowersList = false">
                <div class="followers-content">
                  <div class="followers-header">
                    <h4>粉丝列表</h4>
                    <button @click="showFollowersList = false" class="close-btn">×</button>
                  </div>
                  <div class="followers-list">
                    <div v-for="user in followersList" :key="user.id" class="follower-item">
                      <div class="follower-avatar">{{ user.username?.[0]?.toUpperCase() }}</div>
                      <div class="follower-info">
                        <span class="follower-name">{{ user.nickname || user.username }}</span>
                        <span class="follower-bio">{{ user.bio || '暂无简介' }}</span>
                      </div>
                    </div>
                    <div v-if="followersList.length === 0" class="no-followers">
                      暂无粉丝
                    </div>
                  </div>
                </div>
              </div>

              <button
                v-if="userStore.isLoggedIn && post?.author.id !== userStore.user?.id"
                @click="toggleFollow"
                :disabled="followLoading"
                :class="['follow-btn', { following: isFollowing }]"
              >
                {{ followLoading ? '处理中...' : (isFollowing ? '已关注' : '+ 关注') }}
              </button>
            </div>
          </div>
        </aside>

        <!-- 中间：文章内容 -->
        <main class="main-content">
          <!-- 文章卡片 -->
          <div class="article-card">
            <h1 class="article-title">{{ post.title }}</h1>

            <div class="article-meta">
              <div class="author-info">
                <div class="author-avatar-sm">
                  <span>{{ post.author.nickname?.[0] || post.author.username[0] }}</span>
                </div>
                <span>{{ post.author.nickname || post.author.username }}</span>
              </div>
              <span>{{ formatDate(post.created_at) }}</span>
              <span>{{ post.view_count }} 阅读</span>
              <span>{{ comments.length }} 评论</span>
            </div>

            <div v-if="post.tags.length" class="article-tags">
              <router-link
                v-for="tag in post.tags"
                :key="tag.id"
                :to="`/tag/${tag.slug}`"
                class="tag-item"
              >
                #{{ tag.name }}
              </router-link>
            </div>

            <div v-if="post.cover_image" class="article-cover">
              <img :src="post.cover_image" :alt="post.title" />
            </div>

            <article class="article-content prose-custom" v-html="processedContent"></article>
          </div>

          <!-- 评论区 -->
          <div class="comment-card">
            <h2 class="comment-title">评论 ({{ comments.length }})</h2>

            <!-- 发表评论 -->
            <div v-if="userStore.isLoggedIn" class="comment-form">
              <div v-if="replyTo" class="reply-tip">
                回复评论...
                <button @click="cancelReply">取消</button>
              </div>
              <textarea
                v-model="commentContent"
                placeholder="写下你的评论..."
                class="comment-input"
              ></textarea>
              <div class="comment-submit">
                <button @click="submitComment" :disabled="!commentContent.trim()">发表评论</button>
              </div>
            </div>
            <div v-else class="login-tip">
              <router-link to="/login">登录</router-link> 后参与评论
            </div>

            <!-- 评论列表 -->
            <div class="comment-list">
              <div v-for="comment in comments" :key="comment.id" class="comment-item">
                <div class="comment-avatar">
                  <span>{{ comment.user.nickname?.[0] || comment.user.username[0] }}</span>
                </div>
                <div class="comment-content-wrapper">
                  <div class="comment-body">
                    <div class="comment-header">
                      <span class="comment-author">{{ comment.user.nickname || comment.user.username }}</span>
                      <span class="comment-date">{{ formatDate(comment.created_at) }}</span>
                    </div>
                    <p class="comment-text">{{ comment.content }}</p>
                    <button v-if="userStore.isLoggedIn" @click="setReply(comment.id)" class="reply-btn">回复</button>
                  </div>

                  <!-- 子评论 -->
                  <div v-if="comment.replies?.length" class="reply-list">
                    <div v-for="reply in comment.replies" :key="reply.id" class="reply-item">
                      <span class="reply-author">{{ reply.user.nickname || reply.user.username }}</span>
                      <span class="reply-date">{{ formatDate(reply.created_at) }}</span>
                      <p class="reply-text">{{ reply.content }}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div v-if="comments.length === 0" class="empty-comment">
              暂无评论，快来抢沙发吧~
            </div>
          </div>
        </main>

        <!-- 右侧：目录 -->
        <aside class="right-sidebar">
          <div class="sticky-wrapper">
            <div v-if="tocItems.length > 0" class="toc-card">
              <div class="toc-header">
                <svg class="toc-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h7" />
                </svg>
                <span>目录</span>
              </div>
              <nav class="toc-nav">
                <a
                  v-for="item in tocItems"
                  :key="item.id"
                  @click="scrollToHeading(item.id)"
                  :class="[
                    'toc-item',
                    'level-' + item.level,
                    { active: activeTocId === item.id }
                  ]"
                  :title="item.text"
                >
                  {{ item.text }}
                </a>
              </nav>
            </div>
          </div>
        </aside>
      </div>
    </template>

    <!-- 文章不存在 -->
    <div v-else class="not-found">
      <p>文章不存在</p>
      <router-link to="/">返回首页</router-link>
    </div>
  </div>
</template>

<style scoped>
.post-page {
  min-height: 100vh;
  background-color: #f8fafc;
}

.dark .post-page {
  background-color: #0f172a;
}

.loading-wrapper {
  display: flex;
  justify-content: center;
  padding: 3rem 0;
}

.loading-spinner {
  width: 2.5rem;
  height: 2.5rem;
  border: 4px solid #6366f1;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 三栏布局 */
.post-container {
  display: grid;
  grid-template-columns: 1fr;
  gap: 0.75rem;
  padding: 0.5rem;
  max-width: 100%;
}

@media (min-width: 1024px) {
  .post-container {
    grid-template-columns: 1fr 200px;
    padding: 0.75rem;
  }
}

@media (min-width: 1280px) {
  .post-container {
    grid-template-columns: 180px 1fr 200px;
    padding: 0.75rem 1rem;
  }
}

/* 侧边栏通用 */
.sticky-wrapper {
  position: sticky;
  top: 4.5rem;
}

.left-sidebar,
.right-sidebar {
  display: none;
}

@media (min-width: 1280px) {
  .left-sidebar {
    display: block;
  }
}

@media (min-width: 1024px) {
  .right-sidebar {
    display: block;
  }
}

/* 作者卡片 */
.author-card {
  background: white;
  border-radius: 0.5rem;
  border: 1px solid #e2e8f0;
  padding: 0.875rem;
  text-align: center;
}

.dark .author-card {
  background: #1e293b;
  border-color: #334155;
}

.author-avatar {
  width: 3rem;
  height: 3rem;
  background: linear-gradient(135deg, #818cf8, #a78bfa);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 0.5rem;
}

.author-avatar span {
  color: white;
  font-size: 1.125rem;
  font-weight: 700;
}

.author-name {
  font-weight: 600;
  color: #0f172a;
  margin: 0;
  font-size: 0.875rem;
}

.dark .author-name {
  color: #f1f5f9;
}

.author-bio {
  font-size: 0.75rem;
  color: #64748b;
  margin: 0.25rem 0 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.dark .author-bio {
  color: #94a3b8;
}

.author-stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.5rem;
  margin-top: 0.75rem;
  padding-top: 0.75rem;
  border-top: 1px solid #e2e8f0;
}

.dark .author-stats {
  border-color: #334155;
}

.stat-num {
  font-size: 1rem;
  font-weight: 700;
  color: #0f172a;
}

.dark .stat-num {
  color: #f1f5f9;
}

.stat-label {
  font-size: 0.7rem;
  color: #64748b;
}

.dark .stat-label {
  color: #94a3b8;
}

.stat-item.clickable {
  cursor: pointer;
  transition: background 0.2s;
  border-radius: 0.25rem;
  padding: 0.25rem;
}

.stat-item.clickable:hover {
  background: #f1f5f9;
}

.dark .stat-item.clickable:hover {
  background: #334155;
}

.follow-btn {
  width: 100%;
  margin-top: 0.75rem;
  padding: 0.375rem 0.75rem;
  background: #6366f1;
  color: white;
  border: none;
  border-radius: 0.375rem;
  font-size: 0.75rem;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
}

.follow-btn:hover:not(:disabled) {
  background: #4f46e5;
}

.follow-btn.following {
  background: #e2e8f0;
  color: #64748b;
}

.dark .follow-btn.following {
  background: #334155;
  color: #94a3b8;
}

.follow-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 主内容区 */
.main-content {
  min-width: 0;
}

.article-card {
  background: white;
  border-radius: 0.5rem;
  border: 1px solid #e2e8f0;
  padding: 1.5rem;
}

.dark .article-card {
  background: #1e293b;
  border-color: #334155;
}

.article-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0 0 1rem;
}

.dark .article-title {
  color: #f1f5f9;
}

.article-meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 1rem;
  font-size: 0.875rem;
  color: #64748b;
  padding-bottom: 1rem;
  margin-bottom: 1rem;
  border-bottom: 1px solid #e2e8f0;
}

.dark .article-meta {
  color: #94a3b8;
  border-color: #334155;
}

.author-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.author-avatar-sm {
  width: 1.5rem;
  height: 1.5rem;
  background: linear-gradient(135deg, #818cf8, #a78bfa);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.author-avatar-sm span {
  color: white;
  font-size: 0.75rem;
}

.article-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1.25rem;
}

.tag-item {
  padding: 0.25rem 0.75rem;
  background: #f1f5f9;
  color: #64748b;
  font-size: 0.875rem;
  border-radius: 9999px;
  text-decoration: none;
  transition: color 0.2s;
}

.dark .tag-item {
  background: #334155;
  color: #94a3b8;
}

.tag-item:hover {
  color: #6366f1;
}

.article-cover {
  margin-bottom: 1.5rem;
  border-radius: 0.75rem;
  overflow: hidden;
}

.article-cover img {
  width: 100%;
  height: auto;
}

/* 评论区 */
.comment-card {
  margin-top: 0.75rem;
  background: white;
  border-radius: 0.5rem;
  border: 1px solid #e2e8f0;
  padding: 0.75rem;
}

.dark .comment-card {
  background: #1e293b;
  border-color: #334155;
}

.comment-title {
  font-size: 0.875rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0 0 0.75rem;
}

.dark .comment-title {
  color: #f1f5f9;
}

.comment-form {
  margin-bottom: 0.75rem;
}

.reply-tip {
  font-size: 0.875rem;
  color: #64748b;
  margin-bottom: 0.5rem;
}

.reply-tip button {
  color: #6366f1;
  margin-left: 0.5rem;
  background: none;
  border: none;
  cursor: pointer;
}

.comment-input {
  width: 100%;
  min-height: 100px;
  padding: 0.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 0.5rem;
  resize: none;
  font-size: 0.875rem;
  background: white;
}

.dark .comment-input {
  background: #0f172a;
  border-color: #334155;
  color: #f1f5f9;
}

.comment-submit {
  display: flex;
  justify-content: flex-end;
  margin-top: 0.75rem;
}

.comment-submit button {
  padding: 0.5rem 1.25rem;
  background: #6366f1;
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
}

.comment-submit button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.login-tip {
  padding: 1rem;
  background: #f8fafc;
  border-radius: 0.5rem;
  text-align: center;
  font-size: 0.875rem;
  color: #64748b;
}

.dark .login-tip {
  background: #0f172a;
}

.login-tip a {
  color: #6366f1;
}

.comment-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.comment-item {
  padding: 0.625rem;
  background: #f8fafc;
  border-radius: 0.375rem;
}

.dark .comment-item {
  background: #1e293b;
}

.comment-content {
  display: flex;
  gap: 0.5rem;
}

.comment-avatar {
  width: 1.5rem;
  height: 1.5rem;
  background: linear-gradient(135deg, #818cf8, #a78bfa);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.comment-avatar span {
  color: white;
  font-size: 0.65rem;
}

.comment-body {
  flex: 1;
  min-width: 0;
}

.comment-header {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  margin-bottom: 0.125rem;
}

.comment-author {
  font-weight: 500;
  color: #0f172a;
  font-size: 0.75rem;
}

.dark .comment-author {
  color: #f1f5f9;
}

.comment-date {
  font-size: 0.65rem;
  color: #94a3b8;
}

.comment-text {
  color: #475569;
  font-size: 0.75rem;
  margin: 0;
}

.dark .comment-text {
  color: #cbd5e1;
}

.reply-btn {
  font-size: 0.65rem;
  color: #6366f1;
  background: none;
  border: none;
  margin-top: 0.25rem;
  cursor: pointer;
}

.reply-list {
  margin-top: 0.5rem;
  margin-left: 1.25rem;
  padding-left: 0.75rem;
  border-left: 2px solid #e2e8f0;
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.dark .reply-list {
  border-left-color: #334155;
}

.reply-item {
  padding: 0.375rem 0;
  background: transparent;
}

.dark .reply-item {
  background: transparent;
}

.reply-author {
  font-weight: 500;
  color: #334155;
  font-size: 0.7rem;
}

.dark .reply-author {
  color: #cbd5e1;
}

.reply-date {
  font-size: 0.6rem;
  color: #94a3b8;
  margin-left: 0.25rem;
}

.reply-text {
  color: #475569;
  font-size: 0.7rem;
  margin: 0.125rem 0 0;
}

.dark .reply-text {
  color: #94a3b8;
}

.empty-comment {
  text-align: center;
  padding: 1.5rem;
  color: #94a3b8;
  font-size: 0.875rem;
}

/* 目录卡片 */
.toc-card {
  background: white;
  border-radius: 0.5rem;
  border: 1px solid #e2e8f0;
}

.dark .toc-card {
  background: #1e293b;
  border-color: #334155;
}

.toc-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #e2e8f0;
  font-weight: 600;
  font-size: 0.875rem;
  color: #0f172a;
}

.dark .toc-header {
  border-color: #334155;
  color: #f1f5f9;
}

.toc-icon {
  width: 1rem;
  height: 1rem;
  color: #6366f1;
}

.toc-nav {
  padding: 0.75rem;
  max-height: calc(100vh - 200px);
  overflow-y: auto;
}

.toc-item {
  display: block;
  font-size: 0.875rem;
  color: #64748b;
  padding: 0.375rem 0.5rem;
  border-radius: 0.25rem;
  cursor: pointer;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  transition: all 0.2s;
}

.dark .toc-item {
  color: #94a3b8;
}

.toc-item:hover {
  color: #0f172a;
}

.dark .toc-item:hover {
  color: #f1f5f9;
}

.toc-item.active {
  color: #6366f1;
  background: rgba(99, 102, 241, 0.1);
  font-weight: 500;
}

.toc-item.level-1 { padding-left: 0.5rem; }
.toc-item.level-2 { padding-left: 1rem; }
.toc-item.level-3 { padding-left: 1.5rem; }
.toc-item.level-4 { padding-left: 2rem; }

/* 404 */
.not-found {
  text-align: center;
  padding: 5rem 1rem;
  color: #64748b;
}

.not-found a {
  display: inline-block;
  margin-top: 0.5rem;
  color: #6366f1;
}
</style>
