import axios from 'axios'
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

api.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    const status = error.response?.status
    const detail = error.response?.data?.detail || error.response?.data?.message || error.message

    if (status === 401) {
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
