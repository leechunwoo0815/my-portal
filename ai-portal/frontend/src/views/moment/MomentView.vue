<template>
  <div class="moment-view">
    <div class="moment-header">
      <div class="header-top">
        <h1>社区动态</h1>
        <div class="moment-tabs">
          <button
            :class="['tab-btn', { active: activeTab === 'following' }]"
            @click="switchTab('following')"
          >
            <el-icon><UserFilled /></el-icon>
            关注
          </button>
          <button
            :class="['tab-btn', { active: activeTab === 'all' }]"
            @click="switchTab('all')"
          >
            <el-icon><Monitor /></el-icon>
            全站
          </button>
        </div>
      </div>
      <p class="subtitle">分享你的技术见解和日常</p>
    </div>

    <div class="moment-layout">
      <div class="moment-main">
        <div class="post-box" v-if="authStore.isLoggedIn">
          <el-input
            ref="momentInputRef"
            v-model="newMoment.content"
            type="textarea"
            :rows="3"
            placeholder="分享你的技术见解..."
            maxlength="500"
            show-word-limit
          />
          <div class="post-actions">
            <div class="post-left">
              <el-popover ref="emojiPopoverRef" trigger="click" :width="320" placement="bottom-start">
                <template #reference>
                  <el-button text size="small" class="emoji-btn">😊 表情</el-button>
                </template>
                <div class="emoji-grid">
                  <span v-for="e in emojis" :key="e" class="emoji-item" @click="insertEmoji(e)">{{ e }}</span>
                </div>
              </el-popover>
            </div>
            <el-button type="primary" @click="publishMoment" :loading="publishing">发布</el-button>
          </div>
        </div>

        <div v-if="!authStore.isLoggedIn && activeTab === 'following'" class="login-hint">
          <p>登录后查看关注用户的动态</p>
          <el-button type="primary" size="small" @click="$router.push('/login')">去登录</el-button>
        </div>

        <MomentSkeleton v-if="loading" :count="5" />
        <div v-else class="moment-list">
          <div v-for="moment in moments" :key="moment.id" :data-moment-id="moment.id" class="moment-item">
            <div class="moment-author">
              <el-avatar
                :size="40"
                :src="moment.author?.avatar_url"
                class="clickable-avatar"
                @click="goToUser(moment.author?.user_id)"
              >
                {{ (moment.author?.nickname || moment.author?.username || '?')[0] }}
              </el-avatar>
              <div class="author-info">
                <div class="author-name-row">
                  <span
                    class="author-name clickable"
                    @click="goToUser(moment.author?.user_id)"
                  >{{ moment.author?.nickname || moment.author?.username }}</span>
                  <span
                    v-if="moment.author?.level"
                    class="level-badge"
                    :class="'level-' + Math.min(moment.author.level, 10)"
                  >{{ moment.author.level === 999 ? '管理员' : 'LV' + moment.author.level }}</span>
                </div>
                <span class="moment-time">{{ formatDate(moment.created_at) }}</span>
              </div>
            </div>
            <div class="moment-content">{{ moment.content }}</div>
            <div class="moment-actions">
              <LikeButton :target-type="'moment'" :target-id="moment.id" :count="moment.likes_count" />
              <el-button size="small" text class="comment-btn" @click="toggleComments(moment)">
                <el-icon><ChatDotRound /></el-icon>
                <span>{{ moment.comments_count || 0 }} 评论</span>
              </el-button>
            </div>
            <CommentSection
              v-if="activeCommentId === moment.id"
              :target-type="'moment'"
              :target-id="moment.id"
              autofocus
              class="moment-comments"
              @commented="moment.comments_count = $event"
              @loaded="scrollToComment(moment)"
            />
          </div>
        </div>

        <el-empty v-if="!loading && moments.length === 0" :description="activeTab === 'following' ? '关注的用户还没有发布动态' : '还没有动态'">
          <el-button v-if="authStore.isLoggedIn && activeTab === 'following'" type="primary" size="small" @click="switchTab('all')">看看全站动态</el-button>
        </el-empty>

        <div ref="sentinelRef" class="sentinel" />
        <div v-if="loadingMore" class="loading-more">
          <el-icon class="is-loading"><Loading /></el-icon> 加载中...
        </div>
        <div v-if="noMore && moments.length > 0" class="no-more">-- 已加载全部 --</div>
      </div>

      <aside class="moment-sidebar">
        <el-card>
          <template #header><span>热门话题</span></template>
          <div class="hot-topics">
            <el-tag
              v-for="(topic, i) in hotTopics"
              :key="i"
              :type="(['primary', 'success', 'warning', 'danger', 'info'] as const)[i % 5]"
              class="topic-tag"
            >{{ topic }}</el-tag>
          </div>
        </el-card>
      </aside>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ChatDotRound, UserFilled, Monitor, Loading } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { momentApi } from '@/api/moment'
import { ElMessage } from 'element-plus'
import LikeButton from '@/components/interaction/LikeButton.vue'
import CommentSection from '@/components/CommentSection.vue'
import { MomentSkeleton } from '@/components/skeleton'

const router = useRouter()
const authStore = useAuthStore()
const moments = ref<any[]>([])
const loading = ref(false)
const loadingMore = ref(false)
const noMore = ref(false)
const publishing = ref(false)
const page = ref(1)
const pageSize = 20
const newMoment = ref({ content: '' })
const activeCommentId = ref<number | null>(null)
const activeTab = ref<'following' | 'all'>(authStore.isLoggedIn ? 'following' : 'all')
const momentInputRef = ref<any>(null)
const emojiPopoverRef = ref<any>(null)
const sentinelRef = ref<HTMLElement>()

let pollTimer: ReturnType<typeof setInterval> | null = null
let observer: IntersectionObserver | null = null

const hotTopics = ['AI大模型', 'Vue3', 'Python', '深度学习', '面试题', '开源项目', '前端架构', '后端优化']

const emojis = [
  '😀', '😂', '🤣', '😊', '😍', '🤔', '😎', '🥳',
  '🔥', '👍', '👎', '❤️', '💯', '🎉', '✨', '💪',
  '🚀', '💡', '⚡', '🐛', '💻', '📱', '🎯', '🏆',
  '😭', '🤯', '👀', '🙏', '💀', '🤡', '🐶', '🐱',
]

const insertEmoji = (emoji: string) => {
  newMoment.value.content += emoji
  emojiPopoverRef.value?.hide?.()
  nextTick(() => {
    const ta = momentInputRef.value?.textarea
    if (ta) {
      ta.focus()
      const pos = newMoment.value.content.length
      ta.setSelectionRange(pos, pos)
    }
  })
}

const goToUser = (userId?: number) => {
  if (userId) router.push(`/user/${userId}`)
}

const toggleComments = (moment: any) => {
  activeCommentId.value = activeCommentId.value === moment.id ? null : moment.id
}

const scrollToComment = (moment: any) => {
  nextTick(() => {
    const el = document.querySelector(`[data-moment-id="${moment.id}"]`)
    if (el) {
      const rect = el.getBoundingClientRect()
      const offset = window.scrollY + rect.top - 72
      window.scrollTo({ top: offset, behavior: 'smooth' })
    }
  })
}

const switchTab = (tab: 'following' | 'all') => {
  if (tab === activeTab.value) return
  activeTab.value = tab
  moments.value = []
  page.value = 1
  noMore.value = false
  activeCommentId.value = null
  loadMoments()
}

const loadMoments = async (append = false) => {
  if (loading.value || loadingMore.value || noMore.value) return
  if (append) {
    loadingMore.value = true
  } else {
    loading.value = true
  }
  try {
    const apiFn = activeTab.value === 'following' ? momentApi.listFollowing : momentApi.list
    const res: any = await apiFn(page.value, pageSize)
    const newItems = res.items || []
    if (append) {
      moments.value.push(...newItems)
    } else {
      moments.value = newItems
    }
    if (newItems.length < pageSize) {
      noMore.value = true
    } else {
      page.value++
    }
  } catch {
    if (!append) moments.value = []
  } finally {
    loading.value = false
    loadingMore.value = false
  }
}

const pollNewMoments = async () => {
  if (!document.hidden) {
    try {
      const apiFn = activeTab.value === 'following' ? momentApi.listFollowing : momentApi.list
      const res: any = await apiFn(1, pageSize)
      const newItems = res.items || []
      if (newItems.length > 0) {
        const existingIds = new Set(moments.value.map((m: any) => m.id))
        const fresh = newItems.filter((m: any) => !existingIds.has(m.id))
        if (fresh.length > 0) {
          moments.value.unshift(...fresh)
        }
      }
    } catch {}
  }
}

const publishMoment = async () => {
  if (!newMoment.value.content.trim()) return
  publishing.value = true
  try {
    await momentApi.create({ content: newMoment.value.content.trim() })
    ElMessage.success('发布成功')
    newMoment.value.content = ''
    page.value = 1
    noMore.value = false
    await loadMoments()
  } catch {
    ElMessage.error('发布失败')
  } finally {
    publishing.value = false
  }
}

const formatDate = (v: string) => {
  if (!v) return ''
  const d = new Date(v)
  const now = new Date()
  const diff = now.getTime() - d.getTime()
  const minutes = Math.floor(diff / 60000)
  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}小时前`
  return `${d.getMonth() + 1}月${d.getDate()}日`
}

const setupInfiniteScroll = () => {
  if (!sentinelRef.value) return
  observer = new IntersectionObserver(
    (entries) => {
      if (entries[0].isIntersecting && !loadingMore.value && !noMore.value) {
        loadMoments(true)
      }
    },
    { rootMargin: '200px' },
  )
  observer.observe(sentinelRef.value)
}

onMounted(() => {
  loadMoments()
  setTimeout(setupInfiniteScroll, 500)
  pollTimer = setInterval(pollNewMoments, 15000)
})

onUnmounted(() => {
  observer?.disconnect()
  observer = null
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
})
</script>

<style scoped>
.moment-view { min-height: 100vh; background: var(--app-bg, #f5f7fa); padding: 40px 0; }
.moment-header { text-align: center; margin-bottom: 30px; }
.header-top { display: flex; align-items: center; justify-content: center; gap: 16px; margin-bottom: 8px; }
.moment-header h1 { font-size: 2rem; margin: 0; }
.subtitle { color: var(--app-text-secondary, #909399); }

.moment-tabs {
  display: flex;
  gap: 4px;
  background: var(--app-bg-card, white);
  border: 1px solid var(--app-border, #e4e7ed);
  border-radius: 8px;
  padding: 3px;
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 16px;
  border: none;
  border-radius: 6px;
  background: transparent;
  color: var(--app-text-secondary, #909399);
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s;
  font-family: inherit;
}

.tab-btn.active {
  background: var(--app-accent, #409eff);
  color: #fff;
}

.tab-btn:not(.active):hover {
  color: var(--app-text, #303133);
  background: var(--app-bg-secondary, #f0f0f0);
}

.moment-layout { display: grid; grid-template-columns: 2fr 1fr; gap: 24px; max-width: 1000px; margin: 0 auto; padding: 0 20px; }
.moment-main { min-width: 0; }

.post-box { background: var(--app-bg-card, white); padding: 20px; border-radius: 12px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
.post-actions { display: flex; justify-content: space-between; align-items: center; margin-top: 12px; }
.post-left { display: flex; align-items: center; }
.emoji-btn { font-size: 14px; }

.emoji-grid { display: grid; grid-template-columns: repeat(8, 1fr); gap: 4px; max-height: 200px; overflow-y: auto; }
.emoji-item { font-size: 20px; cursor: pointer; text-align: center; padding: 4px; border-radius: 6px; transition: background 0.15s; }
.emoji-item:hover { background: var(--app-bg-secondary, #f0f0f0); }

.login-hint { text-align: center; padding: 40px 20px; background: var(--app-bg-card, white); border-radius: 12px; margin-bottom: 20px; }
.login-hint p { color: var(--app-text-secondary, #909399); margin-bottom: 12px; }

.moment-list { display: flex; flex-direction: column; gap: 16px; }
.moment-item { background: var(--app-bg-card, white); padding: 20px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
.moment-author { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; }
.clickable-avatar { cursor: pointer; transition: opacity 0.2s; }
.clickable-avatar:hover { opacity: 0.8; }
.author-info { display: flex; flex-direction: column; gap: 2px; }
.author-name-row { display: flex; align-items: center; gap: 8px; }
.author-name { font-weight: 600; font-size: 14px; }
.author-name.clickable { cursor: pointer; }
.author-name.clickable:hover { color: var(--app-accent, #409eff); }

.level-badge {
  font-size: 10px;
  padding: 1px 6px;
  border-radius: 6px;
  color: #fff;
  font-weight: 600;
  letter-spacing: 0.5px;
}
.level-1, .level-2 { background: #909399; }
.level-3, .level-4 { background: #409eff; }
.level-5, .level-6 { background: #67c23a; }
.level-7, .level-8 { background: #e6a23c; }
.level-9, .level-10 { background: #f56c6c; }

.moment-time { font-size: 12px; color: var(--el-text-color-secondary, #909399); }
.moment-content { font-size: 15px; line-height: 1.6; margin-bottom: 12px; white-space: pre-wrap; }
.moment-actions { display: flex; gap: 12px; align-items: center; }
.comment-btn { font-size: 13px; }
.moment-comments { margin-top: 16px; padding-top: 16px; border-top: 1px solid var(--app-border, #e4e7ed); }

.sentinel { height: 1px; }
.loading-more { text-align: center; padding: 16px; color: var(--app-text-secondary, #909399); font-size: 14px; }
.no-more { text-align: center; padding: 24px; color: var(--app-text-secondary, #909399); font-size: 13px; }

.moment-sidebar { position: sticky; top: 80px; }
.hot-topics { display: flex; flex-wrap: wrap; gap: 8px; }
.topic-tag { cursor: pointer; }

@media (max-width: 768px) {
  .moment-layout { grid-template-columns: 1fr; }
  .moment-sidebar { display: none; }
  .header-top { flex-direction: column; gap: 12px; }
}
</style>
