import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { fetchNotifications, getUnreadCount, markNotificationRead, markAllNotificationsRead } from '@/api/notification'
import { ElNotification } from 'element-plus'

export const useNotificationStore = defineStore('notification', () => {
  const notifications = ref<any[]>([])
  const unreadCount = ref(0)
  const loading = ref(false)
  let ws: WebSocket | null = null
  let reconnectTimer: ReturnType<typeof setTimeout> | null = null

  const hasUnread = computed(() => unreadCount.value > 0)

  const loadNotifications = async (params?: Record<string, any>) => {
    loading.value = true
    try {
      const res: any = await fetchNotifications(params)
      notifications.value = res.items || res || []
      if (res.unread_count !== undefined) {
        unreadCount.value = res.unread_count
      }
    } catch { notifications.value = [] }
    finally { loading.value = false }
  }

  const loadUnreadCount = async () => {
    try {
      const res: any = await getUnreadCount()
      unreadCount.value = res.unread_count || 0
    } catch { unreadCount.value = 0 }
  }

  const markRead = async (id: number) => {
    try {
      await markNotificationRead(id)
      const n = notifications.value.find(x => x.id === id)
      if (n) n.is_read = true
      unreadCount.value = Math.max(0, unreadCount.value - 1)
    } catch {}
  }

  const markAllRead = async () => {
    try {
      await markAllNotificationsRead()
      notifications.value.forEach(n => n.is_read = true)
      unreadCount.value = 0
    } catch {}
  }

  const connectWebSocket = () => {
    const token = localStorage.getItem('access_token')
    if (!token || ws) return

    const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsUrl = `${protocol}//${location.host}/api/v1/notification/ws?token=${token}`

    try {
      ws = new WebSocket(wsUrl)

      ws.onopen = () => {
        // 心跳保活
        if (ws) {
          ws.send('ping')
          setInterval(() => {
            if (ws?.readyState === WebSocket.OPEN) ws.send('ping')
          }, 30000)
        }
      }

      ws.onmessage = (event) => {
        if (event.data === 'pong') return
        try {
          const msg = JSON.parse(event.data)
          if (msg.type === 'notification') {
            unreadCount.value++
            // 弹出桌面通知
            ElNotification({
              title: msg.data?.title || '新通知',
              message: msg.data?.content || '',
              type: 'info',
              duration: 4000,
            })
          }
        } catch {}
      }

      ws.onclose = () => {
        ws = null
        // 自动重连（延迟 5 秒）
        if (reconnectTimer) clearTimeout(reconnectTimer)
        reconnectTimer = setTimeout(connectWebSocket, 5000)
      }

      ws.onerror = () => {
        ws?.close()
      }
    } catch {}
  }

  const disconnectWebSocket = () => {
    if (reconnectTimer) {
      clearTimeout(reconnectTimer)
      reconnectTimer = null
    }
    if (ws) {
      ws.close()
      ws = null
    }
  }

  return {
    notifications, unreadCount, loading, hasUnread,
    loadNotifications, loadUnreadCount, markRead, markAllRead,
    connectWebSocket, disconnectWebSocket,
  }
})
