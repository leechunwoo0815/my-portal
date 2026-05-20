<template>
  <div class="message-page">
    <div class="message-sidebar">
      <h3>私信</h3>
      <div v-for="conv in conversations" :key="conv.user_id"
           class="conv-item" :class="{ active: currentUserId === conv.user_id }"
           @click="selectConversation(conv.user_id)">
        <el-avatar :size="40" :src="conv.avatar_url">
          {{ (conv.nickname || conv.username)?.charAt(0) }}
        </el-avatar>
        <div class="conv-info">
          <div class="conv-header">
            <span class="conv-name">{{ conv.nickname || conv.username }}</span>
            <el-tag size="small" v-if="conv.relationship !== '互相关注'">{{ conv.relationship }}</el-tag>
          </div>
          <p class="conv-last">{{ conv.last_message }}</p>
        </div>
        <el-badge :value="conv.unread_count" v-if="conv.unread_count" />
      </div>
      <div v-if="conversations.length === 0" class="empty">暂无私信</div>
    </div>
    <div class="message-content">
      <div v-if="currentUserId" class="chat-area">
        <div class="chat-header">
          <span>{{ currentConv?.nickname || currentConv?.username }}</span>
        </div>
        <div class="chat-messages" ref="messagesRef">
          <div v-for="msg in messages" :key="msg.id"
               class="message-bubble" :class="{ own: msg.sender_id === authStore.user?.id }">
            <el-avatar :size="32" :src="msg.sender_avatar">
              {{ msg.sender_nickname?.charAt(0) }}
            </el-avatar>
            <div class="bubble-content">
              <img v-if="msg.message_type === 'image' && msg.image_url"
                   :src="msg.image_url" class="msg-image" @click="previewImage(msg.image_url)" />
              <p v-if="msg.content">{{ msg.content }}</p>
              <span class="time">{{ new Date(msg.created_at).toLocaleTimeString() }}</span>
            </div>
          </div>
        </div>
        <div class="chat-input">
          <input ref="fileInput" type="file" accept="image/*" style="display:none" @change="onFileSelected" />
          <el-button :icon="Picture" @click="fileInput?.click()" :disabled="uploading" />
          <el-input v-model="newMessage" placeholder="输入消息..." @keyup.enter="sendMessage" />
          <el-button type="primary" @click="sendMessage" :disabled="(!newMessage.trim() && !pendingImage) || uploading">
            {{ uploading ? '上传中...' : '发送' }}
          </el-button>
        </div>
      </div>
      <div v-else class="no-chat">
        <p>选择一个会话开始聊天</p>
      </div>
    </div>

    <el-dialog v-model="previewVisible" width="auto" append-to-body>
      <img :src="previewUrl" style="max-width:90vw;max-height:80vh" />
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'
import { Picture } from '@element-plus/icons-vue'
import { messageApi } from '@/api/message'
import { uploadImage } from '@/api/upload'

const route = useRoute()
const authStore = useAuthStore()
const conversations = ref<any[]>([])
const messages = ref<any[]>([])
const currentUserId = ref<number | null>(null)
const currentConv = ref<any>(null)
const newMessage = ref('')
const messagesRef = ref<HTMLElement>()
const fileInput = ref<HTMLInputElement>()
const pendingImage = ref<string | null>(null)
const uploading = ref(false)
const previewVisible = ref(false)
const previewUrl = ref('')

const loadConversations = async () => {
  try {
    const res: any = await messageApi.getConversations()
    conversations.value = res.items || []
  } catch (e) { console.error(e) }
}

const selectConversation = async (userId: number) => {
  currentUserId.value = userId
  currentConv.value = conversations.value.find(c => c.user_id === userId)
  try {
    messages.value = await messageApi.getConversationMessages(userId) as any
    await messageApi.markAsRead(userId)
    await loadConversations()
    await nextTick()
    if (messagesRef.value) messagesRef.value.scrollTop = messagesRef.value.scrollHeight
  } catch (e) { console.error(e) }
}

const onFileSelected = async (e: Event) => {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file) return
  if (file.size > 10 * 1024 * 1024) {
    ElMessage.warning('图片大小不能超过 10MB')
    return
  }
  uploading.value = true
  try {
    const res: any = await uploadImage(file, 'moment')
    pendingImage.value = res.url || res.data?.url
  } catch {
    ElMessage.error('图片上传失败')
    pendingImage.value = null
  } finally {
    uploading.value = false
    if (fileInput.value) fileInput.value.value = ''
  }
}

const sendMessage = async () => {
  if (!currentUserId.value) return
  const hasText = !!newMessage.value.trim()
  const hasImage = !!pendingImage.value
  if (!hasText && !hasImage) return

  try {
    if (hasImage) {
      await messageApi.send(currentUserId.value, newMessage.value.trim(), 'image', pendingImage.value!)
      pendingImage.value = null
    } else {
      await messageApi.send(currentUserId.value, newMessage.value.trim())
    }
    newMessage.value = ''
    await selectConversation(currentUserId.value)
  } catch (e) { console.error(e); ElMessage.error('发送失败') }
}

const previewImage = (url: string) => {
  previewUrl.value = url
  previewVisible.value = true
}

onMounted(async () => {
  await loadConversations()
  const queryUserId = route.query.userId
  if (queryUserId) {
    await selectConversation(parseInt(queryUserId as string))
  }
})
</script>

<style scoped lang="scss">
.message-page { display: flex; height: calc(100vh - 120px); max-width: 1200px; margin: 0 auto; }
.message-sidebar { width: 300px; border-right: 1px solid var(--app-border); overflow-y: auto; }
.message-sidebar h3 { padding: 16px; margin: 0; }
.conv-item { display: flex; align-items: center; gap: 10px; padding: 12px 16px; cursor: pointer; border-bottom: 1px solid var(--app-border); }
.conv-item:hover, .conv-item.active { background: var(--app-bg-secondary); }
.conv-info { flex: 1; min-width: 0; }
.conv-header { display: flex; align-items: center; gap: 6px; }
.conv-name { font-weight: 500; }
.conv-last { color: var(--app-text-secondary); font-size: 13px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.message-content { flex: 1; display: flex; flex-direction: column; }
.chat-area { display: flex; flex-direction: column; height: 100%; }
.chat-header { padding: 12px 16px; border-bottom: 1px solid var(--app-border); font-weight: 500; }
.chat-messages { flex: 1; overflow-y: auto; padding: 16px; }
.message-bubble { display: flex; gap: 8px; margin-bottom: 12px; }
.message-bubble.own { flex-direction: row-reverse; }
.bubble-content { background: var(--app-bg-secondary); padding: 8px 12px; border-radius: 12px; max-width: 60%; }
.message-bubble.own .bubble-content { background: var(--app-accent); color: white; }
.msg-image { max-width: 240px; max-height: 240px; border-radius: 8px; cursor: pointer; display: block; margin-bottom: 4px; }
.time { font-size: 11px; color: var(--app-text-secondary); }
.chat-input { display: flex; gap: 8px; padding: 12px 16px; border-top: 1px solid var(--app-border); align-items: center; }
.no-chat { display: flex; align-items: center; justify-content: center; height: 100%; color: var(--app-text-secondary); }
.empty { text-align: center; padding: 40px; color: var(--app-text-secondary); }
</style>
