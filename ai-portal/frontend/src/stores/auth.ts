/**
 * 认证状态管理 - Pinia Store
 * 管理：用户信息、Token、登录/登出状态
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { login as loginApi, getCurrentUser } from '@/api/auth'

export interface User {
  id: number
  username: string
  email: string | null
  nickname: string | null
  is_active: boolean
  is_admin: boolean
  avatar_url: string | null
  level: number
  points: number
  total_points: number
  followers_count: number
  following_count: number
}

export const useAuthStore = defineStore('auth', () => {
  const router = useRouter()
  const user = ref<User | null>(null)
  const token = ref<string>(localStorage.getItem('access_token') || '')
  const loading = ref(false)

  const isLoggedIn = computed(() => !!token.value && !!user.value)
  const isAdmin = computed(() => user.value?.is_admin || false)

  const login = async (username: string, password: string, rememberMe: boolean = false) => {
    loading.value = true
    try {
      const res: any = await loginApi(username, password, rememberMe)
      token.value = res.access_token
      localStorage.setItem('access_token', res.access_token)
      await fetchUser()
      return { success: true }
    } catch (error: any) {
      let errorMessage = '登录失败，请稍后重试'
      if (error.response) {
        if (error.response.status === 401) {
          errorMessage = '用户名或密码错误'
        } else if (error.response.status === 500) {
          errorMessage = '服务器内部错误，请稍后重试'
        } else if (error.response.data?.detail) {
          errorMessage = error.response.data.detail
        } else if (error.response.data?.message) {
          errorMessage = error.response.data.message
        }
      } else if (error.request) {
        errorMessage = '服务器无响应，请检查网络连接'
      } else {
        errorMessage = `请求错误: ${error.message}`
      }
      return { success: false, error: errorMessage }
    } finally {
      loading.value = false
    }
  }

  /**
   * 获取当前用户信息
   * 返回: true=成功, false=token无效需重新登录, null=网络错误可重试
   */
  const fetchUser = async (): Promise<boolean | null> => {
    if (!token.value) return false
    try {
      const res: any = await getCurrentUser()
      user.value = res
      return true
    } catch (error: any) {
      if (error.response?.status === 401) {
        forceLogout()
        return false
      }
      return null
    }
  }

  const forceLogout = () => {
    user.value = null
    token.value = ''
    localStorage.removeItem('access_token')
    import('@/stores/chat').then(({ useChatStore }) => {
      useChatStore().$reset()
    })
  }

  const logout = () => {
    forceLogout()
    router.push('/')
  }

  return {
    user,
    token,
    loading,
    isLoggedIn,
    isAdmin,
    login,
    fetchUser,
    forceLogout,
    logout,
  }
})
