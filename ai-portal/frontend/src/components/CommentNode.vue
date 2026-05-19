<template>
  <div :class="['cs-item', depth === 0 ? 'cs-root' : 'cs-reply']">
    <div class="cs-item-hd">
      <span class="cs-user-tag" :class="{ clickable: comment.user_id }" @click="goToUser">
        <img v-if="comment.avatar_url" :src="comment.avatar_url" class="cs-avatar-img" />
        <span v-else class="cs-avatar">{{ comment.emoji || '🙂' }}</span>
        <strong class="cs-username">{{ comment.author_name }}</strong>
        <span class="cs-level" :class="'cs-level-' + Math.min(comment.level || 1, 10)">
          {{ (comment.level || 1) === 999 ? '管理员' : 'LV' + (comment.level || 1) }}
        </span>
        <span v-if="isAuthor" class="cs-author-badge">作者</span>
      </span>
      <span class="cs-time">{{ timeAgo(comment.created_at) }}</span>
    </div>
    <div class="cs-item-content">{{ comment.content }}</div>
    <div class="cs-item-actions">
      <el-link :underline="false" size="small" class="cs-like-btn" @click="$emit('like', comment)">
        {{ comment.liked ? '❤️' : '🤍' }} {{ comment.likes_count || 0 }}
      </el-link>
      <el-link :underline="false" size="small" class="cs-reply-link" @click="toggleReply">💬 回复</el-link>
    </div>

    <div v-if="showReplyForm" class="cs-inline-reply">
      <div class="cs-inline-reply-input">
        <el-input
          ref="inlineReplyRef"
          v-model="replyContent"
          type="textarea"
          :rows="2"
          :placeholder="`回复 ${comment.author_name}...`"
          maxlength="5000"
        />
        <el-popover ref="replyEmojiPopover" placement="bottom-end" trigger="click" width="260" popper-class="cs-emoji-popper">
          <template #reference>
            <el-button size="small" class="cs-inline-emoji-btn" aria-label="插入表情">😊</el-button>
          </template>
          <div class="emoji-grid">
            <span v-for="e in replyEmojis" :key="e" class="emoji-item" @click="insertReplyEmoji(e)">{{ e }}</span>
          </div>
        </el-popover>
      </div>
      <div class="cs-inline-reply-actions">
        <el-button size="small" text @click="cancelReply">取消</el-button>
        <el-button size="small" type="primary" :disabled="!replyContent.trim()" :loading="replySubmitting" @click="submitReply">回复</el-button>
      </div>
    </div>

    <div v-if="comment.replies && comment.replies.length" class="cs-replies">
      <CommentNode
        v-for="child in displayReplies"
        :key="child.id"
        :comment="child"
        :depth="depth + 1"
        :max-replies="maxReplies"
        :time-ago="timeAgo"
        :author-id="authorId"
        @like="(c: any) => $emit('like', c)"
        @submitted="(c: any) => $emit('submitted', c)"
      />
      <el-link
        v-if="comment.replies.length > max && !showAll"
        :underline="false"
        size="small"
        class="cs-more"
        @click="showAll = true"
      >
        更多回复 +
      </el-link>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const props = defineProps<{
  comment: any
  depth: number
  maxReplies?: number
  timeAgo: (t: string) => string
  authorId?: number
}>()

const emit = defineEmits<{
  like: [comment: any]
  submitted: [comment: any]
}>()

const showAll = ref(false)
const max = computed(() => (props.maxReplies ?? 5))
const isAuthor = computed(() => props.authorId && props.comment.user_id === props.authorId)

const goToUser = () => {
  if (props.comment.user_id) router.push(`/user/${props.comment.user_id}`)
}

const showReplyForm = ref(false)
const replyContent = ref('')
const replySubmitting = ref(false)
const inlineReplyRef = ref<any>(null)
const replyEmojiPopover = ref<any>(null)
const replyEmojis = ['😀','😂','👍','❤️','🔥','🎉','💡','🤔','👏','🙏','😊','😍','🚀','⭐','💪','🙌','✨','🎯','💯','😢','🥰','😎','🤩','😈','🎨','🌈','⚡','🦊','🐱','🍀']

const displayReplies = computed(() => {
  if (!props.comment.replies) return []
  if (showAll.value || props.depth >= 2) return props.comment.replies
  return props.comment.replies.slice(0, max.value)
})

const toggleReply = () => {
  showReplyForm.value = !showReplyForm.value
  if (showReplyForm.value) {
    nextTick(() => {
      const ta = inlineReplyRef.value?.textarea || inlineReplyRef.value?.$el?.querySelector('textarea')
      if (ta) ta.focus()
    })
  }
}

const cancelReply = () => {
  showReplyForm.value = false
  replyContent.value = ''
}

const insertReplyEmoji = (emoji: string) => {
  const ta = inlineReplyRef.value?.textarea
  const start = ta?.selectionStart ?? replyContent.value.length
  const end = ta?.selectionEnd ?? replyContent.value.length
  replyContent.value = replyContent.value.slice(0, start) + emoji + replyContent.value.slice(end)
  replyEmojiPopover.value?.hide?.()
  nextTick(() => {
    if (ta) {
      ta.focus()
      const pos = start + emoji.length
      ta.setSelectionRange(pos, pos)
    }
  })
}

const submitReply = async () => {
  if (!replyContent.value.trim()) return
  replySubmitting.value = true
  try {
    emit('submitted', {
      parent_id: props.comment.id,
      content: replyContent.value.trim(),
    })
    showReplyForm.value = false
    replyContent.value = ''
  } finally {
    replySubmitting.value = false
  }
}
</script>

<style scoped>
.cs-item {
  padding: 12px 14px;
  border-radius: 8px;
  background: var(--app-bg-card, #fff);
  border: 1px solid var(--app-border, #e4e7ed);
}

.cs-root {
  background: var(--app-bg-card, #fff);
}

.cs-reply {
  background: var(--app-bg, #f5f7fa);
}

.cs-item-hd {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.cs-user-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 3px 10px;
  border: 1px solid var(--app-border, #e4e7ed);
  border-radius: 16px;
  background: var(--app-bg, #f5f7fa);
}

.cs-user-tag.clickable {
  cursor: pointer;
  transition: border-color 0.2s, background 0.2s;
}

.cs-user-tag.clickable:hover {
  border-color: var(--app-accent, #409eff);
  background: var(--app-accent-light, rgba(64, 158, 255, 0.08));
}

.cs-avatar-img {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  object-fit: cover;
}

.cs-avatar {
  font-size: 16px;
  line-height: 1;
}

.cs-username {
  font-size: 13px;
  font-weight: 600;
  color: var(--app-text, #303133);
}

.cs-level {
  font-size: 10px;
  padding: 1px 6px;
  border-radius: 6px;
  color: #fff;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.cs-level-1, .cs-level-2 { background: #909399; }
.cs-level-3, .cs-level-4 { background: #409eff; }
.cs-level-5, .cs-level-6 { background: #67c23a; }
.cs-level-7, .cs-level-8 { background: #e6a23c; }
.cs-level-9, .cs-level-10 { background: #f56c6c; }

.cs-author-badge {
  font-size: 10px;
  padding: 1px 6px;
  border-radius: 6px;
  font-weight: 600;
  letter-spacing: 0.5px;
  background: var(--app-accent, #409eff);
  color: #fff;
}

.cs-time {
  color: var(--app-text-secondary, #909399);
  font-size: 11px;
  margin-left: auto;
  flex-shrink: 0;
}

.cs-item-content {
  white-space: pre-wrap;
  word-break: break-word;
  font-size: 14px;
  line-height: 1.7;
  margin-bottom: 8px;
  color: var(--app-text, #303133);
}

.cs-item-actions {
  display: flex;
  gap: 16px;
}

.cs-like-btn {
  font-size: 12px;
  transition: color 0.2s;
}

.cs-reply-link {
  font-size: 12px;
}

.cs-inline-reply {
  margin-top: 10px;
  padding: 10px;
  background: var(--app-bg, #f5f7fa);
  border-radius: 8px;
  border: 1px solid var(--app-border, #e4e7ed);
}

.cs-inline-reply-input {
  position: relative;
}

.cs-inline-emoji-btn {
  position: absolute;
  bottom: 6px;
  right: 6px;
  z-index: 2;
  font-size: 16px;
  padding: 2px 6px;
  cursor: pointer;
}

.cs-inline-reply-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 8px;
}

.cs-replies {
  margin-top: 10px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding-left: 20px;
  border-left: 2px solid var(--app-border, #e4e7ed);
}

.cs-more {
  display: block;
  margin-top: 4px;
  text-align: center;
  font-size: 12px;
}
</style>
