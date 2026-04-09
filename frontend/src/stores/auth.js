import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))
  const accessToken = ref(localStorage.getItem('access_token') || null)
  const refreshToken = ref(localStorage.getItem('refresh_token') || null)

  const isAuthenticated = computed(() => !!accessToken.value && !!user.value)
  const userRole = computed(() => user.value?.role || '')
  const userFullName = computed(() => user.value?.full_name || '')

  const ROLE_LEVELS = {
    super_admin: 7, administrator: 6, finance_officer: 5,
    pastor: 5, secretary: 4, cell_leader: 3, data_entry: 2,
  }

  const roleLevel = computed(() => ROLE_LEVELS[userRole.value] || 0)

  function can(...roles) {
    return roles.includes(userRole.value)
  }

  function canLevel(minLevel) {
    return roleLevel.value >= minLevel
  }

  async function login(email, password) {
    const { data } = await authApi.login({ email, password })
    accessToken.value = data.access
    refreshToken.value = data.refresh
    user.value = data.user
    localStorage.setItem('access_token', data.access)
    localStorage.setItem('refresh_token', data.refresh)
    localStorage.setItem('user', JSON.stringify(data.user))
    return data
  }

  async function logout() {
    try {
      if (refreshToken.value) await authApi.logout(refreshToken.value)
    } catch {}
    accessToken.value = null
    refreshToken.value = null
    user.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
  }

  async function fetchMe() {
    const { data } = await authApi.me()
    user.value = data
    localStorage.setItem('user', JSON.stringify(data))
  }

  return { user, accessToken, isAuthenticated, userRole, userFullName, roleLevel, can, canLevel, login, logout, fetchMe }
})
