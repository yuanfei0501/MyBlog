<script setup lang="ts">
import { useDark, useToggle } from '@vueuse/core'
import { onMounted } from 'vue'
import { useUserStore } from '@/stores/user'

const isDark = useDark()
const toggleDark = useToggle(isDark)

const userStore = useUserStore()

onMounted(() => {
  userStore.init()
})
</script>

<template>
  <div class="min-h-screen bg-slate-50 dark:bg-slate-900 transition-colors duration-300">
    <router-view />
  </div>
</template>
