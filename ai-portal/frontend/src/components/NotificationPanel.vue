<template>
  <el-popover placement="bottom-end" :width="popoverWidth" trigger="click" @show="loadNotifications">
    <template #reference>
      <span class="notif-trigger" title="通知">
        <el-badge :value="unreadCount" :hidden="!unreadCount" :max="99">
          <el-icon :size="20"><Bell /></el-icon>
        </el-badge>
      </span>
    </template>
    <div class="notif-panel">
      <div class="notif-header">
        <span>通知 ({{ unreadCount }} 条未读)</span>
        <el-button text size="small" @click="markAll" v-if="unreadCount">全部已读</el-button>
      </div>
      <div v-if="loading" class="notif-loading">加载中...</div>
      <div v-else-if="notifications.length === 0" class="notif-empty">暂无通知</div>
      <div v-else class="notif-list">
        <div
          v-for="item in notifications"
          :key="item.id"
          class="notif-item"
          :class="{ unread: !item.is_read }"
          @click="readItem(item)"
        >
          <el-avatar :size="36" :src="item.from_avatar">
            {{ (item.from_username || 'U').charAt(0) }}
          </el-avatar>
          <div class="notif-body">
            <p>{{ item.content }}</p>
            <span class="notif-time">{{ timeAgo(item.created_at) }}</span>
          </div>
          <el-tag size="small" v-if="item.type === 'follow'">关注</el-tag>
          <el-tag size="small" v-else-if="item.type === 'like'" type="warning">点赞</el-tag>
          <el-tag size="small" v-else-if="item.type === 'comment'" type="info">评论</el-tag>
          <el-tag size="small" v-else-if="item.type === 'message'" type="success">私信</el-tag>
          <el-tag size="small" v-else-if="item.type === 'favorite'" type="danger">收藏</el-tag>
        </div>
      </div>
      <div class="notif-footer">
        <el-button text size="small" @click="$router.push('/admin/notifications')">查看全部</el-button>
      </div>
    </div>
  </el-popover>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { Bell } from '@element-plus/icons-vue'
import { fetchNotifications, markNotificationRead, markAllNotificationsRead, getUnreadCount } from '@/api/notification'

const loading = ref(false)
const notifications = ref<any[]>([])
const unreadCount = ref(0)
const windowWidth = ref(window.innerWidth)
const popoverWidth = computed(() => windowWidth.value < 400 ? windowWidth.value - 32 : 360)

const updateWidth = () => { windowWidth.value = window.innerWidth }
onMounted(() => window.addEventListener('resize', updateWidth))
onUnmounted(() => window.removeEventListener('resize', updateWidth))

const timeAgo = (t: string) => {
  const diff = Date.now() - new Date(t).getTime()
  const m = Math.floor(diff / 60000)
  if (m < 1) return '刚刚'
  if (m < 60) return `${m}分钟前`
  const h = Math.floor(m / 60)
  if (h < 24) return `${h}小时前`
  return new Date(t).toLocaleDateString()
}

const loadNotifications = async () => {
  loading.value = true
  try {
    const res: any = await fetchNotifications({ page: 1, page_size: 10 })
    notifications.value = res.items || []
    unreadCount.value = res.unread_count || 0
  } catch {} finally { loading.value = false }
}

const loadCount = async () => {
  try {
    const res: any = await getUnreadCount()
    unreadCount.value = res.unread_count || 0
  } catch {}
}

const readItem = async (item: any) => {
  if (!item.is_read) {
    try {
      await markNotificationRead(item.id)
      notifications.value = notifications.value.map(n =>
        n.id === item.id ? { ...n, is_read: true } : n
      )
      unreadCount.value = Math.max(0, unreadCount.value - 1)
    } catch {}
  }
}

const markAll = async () => {
  try {
    await markAllNotificationsRead()
    unreadCount.value = 0
    notifications.value = notifications.value.map(n => ({ ...n, is_read: true }))
  } catch {}
}

onMounted(loadCount)
</script>

<style scoped>
.notif-trigger { display: inline-flex; cursor: pointer; color: var(--app-text-secondary); }
.notif-trigger:hover { color: var(--app-accent); }
.notif-panel { max-height: 420px; display: flex; flex-direction: column; }
.notif-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; font-weight: 600; font-size: 14px; }
.notif-loading, .notif-empty { text-align: center; padding: 30px 0; color: var(--text-secondary); font-size: 13px; }
.notif-list { flex: 1; overflow-y: auto; max-height: 320px; }
.notif-item { display: flex; align-items: center; gap: 10px; padding: 10px 8px; border-radius: 6px; cursor: pointer; }
.notif-item:hover { background: var(--app-bg-secondary, #f5f7fa); }
.notif-item.unread { background: rgba(64, 158, 255, 0.05); }
.notif-body { flex: 1; min-width: 0; }
.notif-body p { margin: 0; font-size: 13px; line-height: 1.5; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.notif-time { font-size: 11px; color: var(--app-text-secondary); }
.notif-footer { text-align: center; margin-top: 8px; padding-top: 8px; border-top: 1px solid var(--app-border); }
</style>
