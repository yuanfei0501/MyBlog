<script setup lang="ts">
import { ref } from 'vue'

const settings = ref({
  siteName: 'MyBlog',
  siteDescription: '一个现代化的博客系统',
  postsPerPage: 10,
  allowComments: true,
  requireApproval: true,
})

const saving = ref(false)

async function handleSave() {
  saving.value = true
  try {
    // 保存设置（实际应该调用 API）
    await new Promise(resolve => setTimeout(resolve, 500))
    alert('设置已保存')
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div>
    <h1 class="text-2xl font-bold text-slate-800 dark:text-slate-100 mb-6">系统设置</h1>

    <div class="card p-6 max-w-2xl">
      <div class="space-y-6">
        <!-- 站点名称 -->
        <div>
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">站点名称</label>
          <input v-model="settings.siteName" type="text" class="input" />
        </div>

        <!-- 站点描述 -->
        <div>
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">站点描述</label>
          <textarea v-model="settings.siteDescription" class="input" rows="3"></textarea>
        </div>

        <!-- 每页文章数 -->
        <div>
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">每页文章数</label>
          <input v-model.number="settings.postsPerPage" type="number" min="5" max="50" class="input w-32" />
        </div>

        <!-- 评论设置 -->
        <div class="space-y-3">
          <div class="flex items-center justify-between">
            <span class="text-sm text-slate-600 dark:text-slate-300">允许评论</span>
            <button
              @click="settings.allowComments = !settings.allowComments"
              :class="[
                'w-10 h-6 rounded-full transition-colors',
                settings.allowComments ? 'bg-primary-500' : 'bg-slate-300 dark:bg-slate-600'
              ]"
            >
              <span
                :class="[
                  'block w-4 h-4 bg-white rounded-full transition-transform',
                  settings.allowComments ? 'translate-x-5' : 'translate-x-1'
                ]"
              ></span>
            </button>
          </div>
          <div class="flex items-center justify-between">
            <span class="text-sm text-slate-600 dark:text-slate-300">评论需要审核</span>
            <button
              @click="settings.requireApproval = !settings.requireApproval"
              :class="[
                'w-10 h-6 rounded-full transition-colors',
                settings.requireApproval ? 'bg-primary-500' : 'bg-slate-300 dark:bg-slate-600'
              ]"
            >
              <span
                :class="[
                  'block w-4 h-4 bg-white rounded-full transition-transform',
                  settings.requireApproval ? 'translate-x-5' : 'translate-x-1'
                ]"
              ></span>
            </button>
          </div>
        </div>

        <!-- 保存按钮 -->
        <div class="pt-4">
          <button @click="handleSave" :disabled="saving" class="btn-primary">
            {{ saving ? '保存中...' : '保存设置' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
