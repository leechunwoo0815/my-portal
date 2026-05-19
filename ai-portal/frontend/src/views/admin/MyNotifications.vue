<template>
  <div class="my-notifications">
    <div class="toolbar">
      <el-button @click="markAllRead" :disabled="unreadCount === 0">全部已读</el-button>
      <span v-if="unreadCount > 0" style="color:var(--app-accent)">({{ unreadCount }} 条未读)</span>
    </div>

    <div v-if="notifications.length === 0" class="empty">暂无通知</div>

    <div v-for="notif in notifications" :key="notif.id" class="notif-item" role="button" tabindex="0" :class="{ unread: !notif.is_read }" @click="readNotification(notif)" @keydown.enter="readNotification(notif)">
      <el-avatar :size="36" :src="notif.from_avatar">{{ notif.from_username?.charAt(0) }}</el-avatar>
      <div class="notif-content">
        <p>{{ notif.content }}</p>
        <span class="notif-time">{{ new Date(notif.created_at).toLocaleString() }}</span>
      </div>
      <el-tag size="small" v-if="notif.type === 'follow'">关注</el-tag>
      <el-tag size="small" v-else-if="notif.type === 'like'" type="warning">点赞</el-tag>
      <el-tag size="small" v-else-if="notif.type === 'comment'" type="info">评论</el-tag>
      <el-tag size="small" v-else-if="notif.type === 'message'" type="success">私信</el-tag>
    </div>

    <el-pagination v-model:current-page="page" :page-size="20" :total="total" layout="prev, pager, next" @current-change="loadNotifications" style="margin-top:16px" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { fetchNotifications, markNotificationRead, markAllNotificationsRead } from '@/api/notification'

const notifications = ref<any[]>([])
const page = ref(1)
const total = ref(0)
const unreadCount = ref(0)

const loadNotifications = async () => {
  try {
    const res: any = await fetchNotifications({ page: page.value })
    notifications.value = res.items || []
    total.value = res.total || 0
    unreadCount.value = res.unread_count || 0
  } catch (e) {}
}

const readNotification = async (notif: any) => {
  if (!notif.is_read) {
    await markNotificationRead(notif.id)
    notif.is_read = true
    unreadCount.value = Math.max(0, unreadCount.value - 1)
  }
}

const markAllRead = async () => {
  await markAllNotificationsRead()
  loadNotifications()
}

onMounted(loadNotifications)
</script>

<style scoped>
.toolbar { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; }
.notif-item { display: flex; align-items: center; gap: 12px; padding: 12px; border-bottom: 1px solid var(--app-border); cursor: pointer; }
.notif-item:hover { background: var(--app-bg-secondary); }
.notif-item.unread { background: rgba(64, 158, 255, 0.05); }
.notif-content { flex: 1; }
.notif-content p { margin: 0; }
.notif-time { font-size: 12px; color: var(--app-text-secondary); }
.empty { text-align: center; padding: 40px; color: var(--app-text-secondary); }
</style>
