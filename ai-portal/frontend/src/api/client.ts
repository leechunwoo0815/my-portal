import axios, { AxiosRequestConfig, AxiosResponse } from 'axios'
import { ElMessage } from 'element-plus'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 30000,
})

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error),
)

let _globalLogoutHandler: (() => void) | null = null

export function setGlobalLogoutHandler(handler: () => void) {
  _globalLogoutHandler = handler
}

// ---- Token refresh machinery ----
let isRefreshing = false
let pendingQueue: Array<{
  resolve: (token: string) => void
  reject: (error: any) => void
}> = []

function processPendingQueue(error: any, token: string | null) {
  pendingQueue.forEach(({ resolve, reject }) => {
    if (error || !token) {
      reject(error)
    } else {
      resolve(token)
    }
  })
  pendingQueue = []
}

async function attemptRefresh(): Promise<string> {
  const refreshToken = localStorage.getItem('refresh_token')
  if (!refreshToken) throw new Error('No refresh token')

  // Use a raw axios call to avoid interceptor loop
  const resp = await axios.post(
    (import.meta.env.VITE_API_BASE_URL || '/api') + '/v1/auth/refresh',
    { refresh_token: refreshToken },
    { timeout: 10000 },
  )
  const data = resp.data?.data || resp.data
  const newAccessToken = data.access_token
  const newRefreshToken = data.refresh_token

  localStorage.setItem('access_token', newAccessToken)
  if (newRefreshToken) {
    localStorage.setItem('refresh_token', newRefreshToken)
  }
  return newAccessToken
}

api.interceptors.response.use(
  (response) => {
    return response.data
  },
  async (error) => {
    const originalConfig = error.config
    const status = error.response?.status

    // 401 and not already retried → try refresh
    if (status === 401 && !originalConfig._retried) {
      if (isRefreshing) {
        // Another refresh is in progress, queue this request
        return new Promise((resolve, reject) => {
          pendingQueue.push({
            resolve: (newToken: string) => {
              originalConfig.headers.Authorization = `Bearer ${newToken}`
              originalConfig._retried = true
              resolve(api(originalConfig))
            },
            reject,
          })
        })
      }

      isRefreshing = true
      originalConfig._retried = true

      try {
        const newToken = await attemptRefresh()
        processPendingQueue(null, newToken)
        originalConfig.headers.Authorization = `Bearer ${newToken}`
        return api(originalConfig)
      } catch (refreshError) {
        processPendingQueue(refreshError, null)
        if (_globalLogoutHandler) {
          _globalLogoutHandler()
        }
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }

    // Other errors
    const detail = error.response?.data?.detail || error.response?.data?.message || error.message

    if (status === 401) {
      // Already retried, force logout
      if (_globalLogoutHandler) {
        _globalLogoutHandler()
      }
    } else if (status === 403) {
      ElMessage.warning('权限不足')
    } else if (status === 404) {
      ElMessage.warning('请求的资源不存在')
    } else if (status === 422) {
      const errors = error.response?.data?.detail
      if (Array.isArray(errors)) {
        const msgs = errors.map((e: any) => e.msg || String(e)).join('; ')
        ElMessage.error(`参数错误: ${msgs}`)
      } else {
        ElMessage.error(typeof detail === 'string' ? detail : '请求参数错误')
      }
    } else if (status === 500) {
      ElMessage.error('服务器内部错误，请稍后重试')
    } else if (!error.response) {
      ElMessage.error('网络连接失败，请检查网络')
    }

    return Promise.reject(error)
  },
)

export default api
