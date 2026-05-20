import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './assets/styles/global.scss'
import { ElNotification } from 'element-plus'
import { setGlobalLogoutHandler } from '@/api/client'

const app = createApp(App)

app.use(createPinia())

import { useThemeStore } from '@/stores/theme'
const themeStore = useThemeStore()
themeStore.initTheme()

app.use(router)

// 如果已登录，连接 WebSocket 通知
if (localStorage.getItem('access_token')) {
  import('./stores/notification').then(({ useNotificationStore }) => {
    useNotificationStore().connectWebSocket()
  })
}

setGlobalLogoutHandler(() => {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  router.push('/login')
})
// ===== 全局错误处理 =====
type LogLevel = 'debug' | 'info' | 'warn' | 'error'

interface LogPayload {
  level: LogLevel
  message: string
  data?: any
  timestamp: string
  url?: string
}

const log = (level: LogLevel, message: string, data?: any) => {
  const payload: LogPayload = {
    level,
    message,
    data,
    timestamp: new Date().toISOString(),
    url: window.location.href,
  }
  // 开发环境输出到控制台
  if (import.meta.env.DEV) {
    const fn = console[level] || console.log
    const prefix = `%c[${level.toUpperCase()}]`
    const style = level === 'error' ? 'color:#f56c6c;font-weight:bold'
      : level === 'warn' ? 'color:#e6a23c;font-weight:bold'
      : 'color:#909399'
    fn(prefix, style, message, data || '')
  }
}

// Vue 全局错误捕获
app.config.errorHandler = (err, instance, info) => {
  log('error', `Vue错误: ${info}`, {
    error: (err as Error).message,
    stack: (err as Error).stack,
  })
  if (import.meta.env.PROD) {
    ElNotification({
      title: '页面异常',
      message: '页面发生错误，请刷新重试',
      type: 'error',
      duration: 5000,
    })
  }
}

// 未捕获的 Promise 异常
window.onunhandledrejection = (event: PromiseRejectionEvent) => {
  log('error', '未捕获的Promise异常', {
    message: (event.reason as any)?.message || String(event.reason),
    stack: (event.reason as any)?.stack,
  })
}

// 全局 JS 运行时错误
window.onerror = (message, source, lineno, colno, error) => {
  log('error', '全局JS运行时错误', {
    message: String(message),
    source,
    lineno,
    colno,
    stack: error?.stack,
  })
  return true
}

(window as any).__LOG = log

app.mount('#app')
