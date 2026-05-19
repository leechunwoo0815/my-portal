<template>
  <div class="notification-view">
    <div class="notification-header">
      <h2>通知中心</h2>
      <el-button size="small" @click="markAllRead" :disabled="!notifications.length">全部已读</el-button>
    </div>

    <div v-loading="loading">
      <div v-if="notifications.length === 0 && !loading">
        <el-empty description="暂无通知" />
      </div>
      <div v-else class="notification-list">
        <div
          v-for="notif in notifications"
          :key="notif.id"
          class="notification-item"
          :class="{ unread: !notif.is_read }"
          @click="handleClick(notif)"
        >
          <div class="notification-item__dot" v-if="!notif.is_read" />
          <div class="notification-item__content">
            <div class="notification-item__title">{{ notif.title }}</div>
            <div class="notification-item__text" v-if="notif.content">{{ notif.content }}</div>
            <div class="notification-item__time">{{ formatDate(notif.created_at) }}</div>
          </div>
        </div>
      </div>

      <el-pagination
        v-if="total > pageSize"
        v-model:current-page="page"
        :page-size="pageSize"
        :total="total"
        layout="prev, pager, next"
        @current-change="loadNotifications"
        class="pagination"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { fetchNotifications, markNotificationRead, markAllNotificationsRead } from '@/api/notification'
import { ElMessage } from 'element-plus'

const router = useRouter()
const notifications = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const loading = ref(false)

const loadNotifications = async () => {
  loading.value = true
  try {
    const res: any = await fetchNotifications({ page: page.value, page_size: pageSize.value })
    notifications.value = res.items || res || []
    total.value = res.total || notifications.value.length
  } catch {
    notifications.value = []
  } finally {
    loading.value = false
  }
}

const handleClick = async (notif: any) => {
  if (!notif.is_read) {
    try {
      await markNotificationRead(notif.id)
      notif.is_read = true
    } catch {}
  }
  if (notif.target_type && notif.target_id) {
    const pathMap: Record<string, string> = {
      blog: '/blog',
      news: '/news',
      product: '/products',
      solution: '/solutions',
    }
    const basePath = pathMap[notif.target_type]
    if (basePath) {
      router.push(`${basePath}/${notif.target_id}`)
    }
  }
}

const markAllRead = async () => {
  try {
    await markAllNotificationsRead()
    notifications.value.forEach(n => n.is_read = true)
    ElMessage.success('已全部标记为已读')
  } catch {
    ElMessage.error('操作失败')
  }
}

const formatDate = (v: string) => {
  if (!v) return ''
  const d = new Date(v)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

onMounted(loadNotifications)
</script>

<style scoped>
.notification-view {
  max-width: 700px;
  margin: 0 auto;
}
.notification-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.notification-header h2 {
  margin: 0;
}
.notification-item {
  display: flex;
  gap: 12px;
  padding: 16px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
  border-bottom: 1px solid var(--el-border-color-lighter);
  position: relative;
}
.notification-item:hover {
  background: var(--el-fill-color-light);
}
.notification-item.unread {
  background: var(--el-color-primary-light-9);
}
.notification-item__dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--el-color-primary);
  margin-top: 6px;
  flex-shrink: 0;
}
.notification-item__content {
  flex: 1;
}
.notification-item__title {
  font-size: 14px;
  font-weight: 500;
}
.notification-item__text {
  font-size: 13px;
  color: var(--el-text-color-secondary);
  margin-top: 4px;
}
.notification-item__time {
  font-size: 12px;
  color: var(--el-text-color-placeholder);
  margin-top: 4px;
}
.pagination {
  margin-top: 24px;
  justify-content: center;
}
</style>
