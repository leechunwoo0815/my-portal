import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { fetchNotifications, getUnreadCount, markNotificationRead, markAllNotificationsRead } from '@/api/notification'

export const useNotificationStore = defineStore('notification', () => {
  const notifications = ref<any[]>([])
  const unreadCount = ref(0)
  const loading = ref(false)

  const hasUnread = computed(() => unreadCount.value > 0)

  const loadNotifications = async (params?: Record<string, any>) => {
    loading.value = true
    try {
      const res: any = await fetchNotifications(params)
      notifications.value = res.items || res || []
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

  return { notifications, unreadCount, loading, hasUnread, loadNotifications, loadUnreadCount, markRead, markAllRead }
})
