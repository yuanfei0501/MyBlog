import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { CurrentUser } from '@/types'
import { authApi } from '@/api'

export const useUserStore = defineStore('user', () => {
  const user = ref<CurrentUser | null>(null)
  const token = ref<string | null>(localStorage.getItem('access_token'))

  const isLoggedIn = computed(() => !!user.value)
  const isAdmin = computed(() => user.value?.role === 'admin')

  async function login(username: string, password: string) {
    const { data } = await authApi.login({ username, password })
    token.value = data.access_token
    localStorage.setItem('access_token', data.access_token)
    localStorage.setItem('refresh_token', data.refresh_token)
    await fetchUser()
  }

  async function fetchUser() {
    if (!token.value) return
    try {
      const { data } = await authApi.getMe()
      user.value = data
    } catch {
      logout()
    }
  }

  function logout() {
    user.value = null
    token.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  function init() {
    if (token.value) {
      fetchUser()
    }
  }

  return {
    user,
    token,
    isLoggedIn,
    isAdmin,
    login,
    fetchUser,
    logout,
    init,
  }
})
