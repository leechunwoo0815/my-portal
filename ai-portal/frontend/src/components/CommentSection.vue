<template>
  <div class="comment-section">
    <h3 class="cs-title">💬 评论 ({{ totalCount }})</h3>

    <div class="cs-form">
      <div class="cs-form-row">
        <el-popover placement="bottom" trigger="click" width="260" popper-class="cs-emoji-popper">
          <template #reference>
            <el-button size="small" class="cs-avatar-btn" aria-label="选择头像表情">{{ form.avatar || '🙂' }}</el-button>
          </template>
          <div class="emoji-grid">
            <span v-for="e in avatarList" :key="e" class="emoji-item" @click="form.avatar = e">{{ e }}</span>
          </div>
        </el-popover>
        <span class="cs-identity">
          <template v-if="authStore.isLoggedIn">
            以 <strong>{{ authStore.user?.nickname || authStore.user?.username }}</strong> 身份评论
          </template>
          <template v-else>
            以 <strong>游客</strong> 身份评论
          </template>
        </span>
      </div>
      <div class="cs-textarea-wrap">
        <el-input ref="contentRef" v-model="form.content" type="textarea" :rows="3" placeholder="输入评论内容" maxlength="5000" show-word-limit />
        <el-popover ref="emojiPopoverRef" placement="bottom-end" trigger="click" width="260" popper-class="cs-emoji-popper">
          <template #reference>
            <el-button size="small" class="cs-emoji-trigger" aria-label="插入表情">😊</el-button>
          </template>
          <div class="emoji-grid">
            <span v-for="e in emojiList" :key="e" class="emoji-item" @click="insertEmoji(e)">{{ e }}</span>
          </div>
        </el-popover>
      </div>
      <div class="cs-form-actions">
        <el-button type="primary" size="small" :loading="submitting" :disabled="!form.content.trim()" @click="submitRoot">发布评论</el-button>
      </div>
    </div>

    <div v-if="loading" class="cs-loading">加载评论中...</div>
    <div v-else-if="comments.length === 0" class="cs-empty">暂无评论，快来抢沙发吧～</div>

    <div v-else class="cs-list">
      <CommentNode
        v-for="item in comments"
        :key="item.id"
        :comment="item"
        :depth="0"
        :time-ago="timeAgo"
        :author-id="authorId"
        @like="handleLike"
        @submitted="handleInlineReply"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch, nextTick, onMounted } from 'vue'
import { listComments, createComment, likeComment } from '@/api/comment'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import CommentNode from './CommentNode.vue'

const props = defineProps<{ targetType: string; targetId: number; authorId?: number; autofocus?: boolean }>()

const emit = defineEmits<{ commented: [count: number]; loaded: [] }>()

const authStore = useAuthStore()

onMounted(() => {
  if (props.autofocus) {
    nextTick(() => {
      const ta = contentRef.value?.textarea || contentRef.value?.$el?.querySelector('textarea')
      if (ta) ta.focus()
    })
  }
})

const comments = ref<any[]>([])
const loading = ref(false)
const submitting = ref(false)
const totalCount = ref(0)
const contentRef = ref<any>(null)
const emojiPopoverRef = ref<any>(null)
const likeLoadingMap = ref<Record<number, boolean>>({})

const avatarList = ['😀','😃','😎','🤩','🥳','😺','🦊','🐱','🐶','🐼','🐨','🦁','🐯','🦄','🐧','🐸','🐙','🦋','🌈','⭐','🔥','🎯','💎','🎩','👑','🧑‍💻','👨‍🎨','🧑‍🚀','🧑‍🏫','🧑‍🎤','🧙','🧝','🦸','🧚','🤖','👾','🎃','👻']
const emojiList = ['😀','😂','👍','❤️','🔥','🎉','💡','🤔','👏','🙏','😊','😍','🚀','⭐','💪','🙌','✨','🎯','💯','😢','🥰','😎','🤩','😈','🎨','🌈','⚡','🦊','🐱','🍀']

const form = reactive({ content: '', avatar: '' })

const timeAgo = (t: string) => {
  const diff = Date.now() - new Date(t).getTime()
  const m = Math.floor(diff / 60000)
  if (m < 1) return '刚刚'
  if (m < 60) return `${m}分钟前`
  const h = Math.floor(m / 60)
  if (h < 24) return `${h}小时前`
  const d = Math.floor(h / 24)
  if (d < 30) return `${d}天前`
  return new Date(t).toLocaleDateString()
}

const loadComments = async () => {
  loading.value = true
  try {
    const data = await listComments(props.targetType, props.targetId)
    comments.value = Array.isArray(data) ? data : []
    totalCount.value = countAll(comments.value)
  } catch (e) { console.error(e); comments.value = []; totalCount.value = 0 }
  finally {
    loading.value = false
    emit('loaded')
  }
}

const countAll = (list: any[]): number => {
  let c = 0
  for (const item of list) {
    c++
    if (item.replies) c += countAll(item.replies)
  }
  return c
}

const insertEmoji = (emoji: string) => {
  const ta = contentRef.value?.textarea
  const start = ta?.selectionStart ?? form.content.length
  const end = ta?.selectionEnd ?? form.content.length
  form.content = form.content.slice(0, start) + emoji + form.content.slice(end)
  emojiPopoverRef.value?.hide?.()
  nextTick(() => {
    if (ta) {
      ta.focus()
      const pos = start + emoji.length
      ta.setSelectionRange(pos, pos)
    }
  })
}

const submitRoot = async () => {
  if (!form.content.trim()) return
  submitting.value = true
  try {
    await createComment(props.targetType, props.targetId, {
      content: form.content.trim(),
      emoji: form.avatar || undefined,
    })
    form.content = ''
    form.avatar = ''
    ElMessage.success('评论发布成功')
    await loadComments()
    emit('commented', totalCount.value)
  } catch { ElMessage.error('发布失败') }
  finally { submitting.value = false }
}

const handleInlineReply = async (data: { parent_id: number; content: string }) => {
  try {
    await createComment(props.targetType, props.targetId, {
      content: data.content,
      parent_id: data.parent_id,
    })
    ElMessage.success('回复成功')
    await loadComments()
    emit('commented', totalCount.value)
  } catch { ElMessage.error('回复失败') }
}

const handleLike = async (item: any) => {
  if (likeLoadingMap.value[item.id]) return
  likeLoadingMap.value[item.id] = true
  try {
    const res: any = await likeComment(item.id)
    item.likes_count = res.likes_count
    item.liked = res.liked
  } catch (e) { console.error(e); ElMessage.error('操作失败') } finally {
    likeLoadingMap.value[item.id] = false
  }
}

watch(() => [props.targetId, props.targetType], loadComments, { immediate: true })
</script>

<style scoped>
.comment-section { margin-top: 20px; padding-top: 16px; border-top: 1px solid var(--app-border, #e4e7ed); }
.cs-title { font-size: 16px; margin: 0 0 16px; color: var(--app-text, #303133); }
.cs-form { margin-bottom: 20px; }
.cs-form-row { display: flex; gap: 8px; margin-bottom: 8px; align-items: center; }
.cs-avatar-btn { font-size: 20px; padding: 2px 8px; cursor: pointer; }
.cs-textarea-wrap { position: relative; }
.cs-emoji-trigger { position: absolute; bottom: 30px; right: 8px; z-index: 2; font-size: 18px; padding: 2px 6px; cursor: pointer; }
.cs-form-actions { display: flex; justify-content: flex-end; align-items: center; margin-top: 8px; }
.cs-loading, .cs-empty { text-align: center; padding: 30px 0; color: var(--app-text-secondary, #909399); font-size: 14px; }
.cs-list { display: flex; flex-direction: column; gap: 12px; }
.cs-identity { font-size: 13px; color: var(--app-text-secondary, #909399); }
.cs-identity strong { color: var(--app-accent, #409eff); }
</style>
<style>
.cs-emoji-popper { padding: 8px; }
.cs-emoji-popper .emoji-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 4px; }
.cs-emoji-popper .emoji-item { font-size: 24px; cursor: pointer; text-align: center; padding: 4px; border-radius: 4px; }
.cs-emoji-popper .emoji-item:hover { background: var(--el-fill-color-light); }
</style>
