<template>
  <div class="feed-view">
    <div class="feed-header">
      <div class="header-left">
        <h1 class="font-mono">[ 动态流 ]</h1>
        <span class="feed-subtitle">关注用户的内容动态</span>
      </div>
      <div class="feed-tabs">
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

    <div class="feed-content" v-loading="loading && items.length === 0">
      <template v-if="items.length === 0 && !loading">
        <div class="empty-state">
          <div class="empty-icon">📡</div>
          <p v-if="activeTab === 'following'">还没有关注任何用户，去发现有趣的人吧</p>
          <p v-else>暂无动态</p>
          <el-button v-if="activeTab === 'following'" type="primary" @click="$router.push('/moment')">发现用户</el-button>
        </div>
      </template>

      <template v-else>
        <div
          v-for="item in items"
          :key="`${item.content_type}-${item.id}`"
          :data-feed-key="`${item.content_type}-${item.id}`"
          class="feed-item"
        >
          <div class="feed-item-header">
            <el-avatar
              :size="36"
              :src="item.author_avatar"
              class="clickable-avatar"
              @click="goToUser(item.author_id)"
            >
              {{ (item.author_name || '').charAt(0) }}
            </el-avatar>
            <div class="feed-item-meta">
              <div class="feed-author-row">
                <span
                  class="feed-author font-mono clickable"
                  @click="goToUser(item.author_id)"
                >{{ item.author_name }}</span>
                <span
                  v-if="item.author_level"
                  class="level-badge"
                  :class="'level-' + Math.min(item.author_level, 10)"
                >{{ item.author_level === 999 ? '管理员' : 'LV' + item.author_level }}</span>
              </div>
              <span class="feed-time">{{ formatTime(item.created_at) }}</span>
            </div>
            <el-tag size="small" :type="contentTypeMap[item.content_type]?.type || 'info'" effect="plain" class="feed-type-tag">
              {{ contentTypeMap[item.content_type]?.label || item.content_type }}
            </el-tag>
          </div>

          <div class="feed-item-body" role="button" tabindex="0" @click="goToDetail(item)" @keydown.enter="goToDetail(item)">
            <h3 v-if="item.title" class="feed-title">{{ item.title }}</h3>
            <p class="feed-summary">{{ item.summary || item.content }}</p>
          </div>

          <div class="feed-item-footer">
            <LikeButton
              :target-type="item.content_type"
              :target-id="item.id"
              :count="item.likes_count || 0"
            />
            <el-button size="small" text @click="toggleComments(item)">
              <el-icon><ChatDotRound /></el-icon> {{ item.comments_count || 0 }}
            </el-button>
          </div>

          <CommentSection
            v-if="activeCommentKey === `${item.content_type}-${item.id}`"
            :target-type="item.content_type"
            :target-id="item.id"
            autofocus
            class="feed-comments"
            @commented="item.comments_count = $event"
            @loaded="scrollToComment(item)"
          />
        </div>

        <div ref="sentinelRef" class="feed-sentinel" />

        <div v-if="loadingMore" class="loading-more">
          <div class="skeleton-card" v-for="i in 3" :key="i">
            <div class="skeleton-header">
              <div class="skeleton-avatar" />
              <div class="skeleton-lines">
                <div class="skeleton-line w-24" />
                <div class="skeleton-line w-16" />
              </div>
            </div>
            <div class="skeleton-body">
              <div class="skeleton-line w-full" />
              <div class="skeleton-line w-3/4" />
            </div>
          </div>
        </div>

        <div v-if="noMore" class="no-more font-mono">
          -- 已加载全部 --
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { UserFilled, Monitor, ChatDotRound } from '@element-plus/icons-vue'
import { feedApi } from '@/api/feed'
import { useAuthStore } from '@/stores/auth'
import LikeButton from '@/components/interaction/LikeButton.vue'
import CommentSection from '@/components/CommentSection.vue'

const router = useRouter()
const authStore = useAuthStore()

const activeTab = ref<'following' | 'all'>('all')
const items = ref<any[]>([])
const loading = ref(false)
const loadingMore = ref(false)
const noMore = ref(false)
const page = ref(1)
const pageSize = 20
const sentinelRef = ref<HTMLElement>()
const activeCommentKey = ref<string | null>(null)

const contentTypeMap: Record<string, { label: string; type: '' | 'primary' | 'success' | 'warning' | 'danger' | 'info' }> = {
  blog: { label: '博客', type: 'primary' },
  moment: { label: '动态', type: 'success' },
  news: { label: '资讯', type: 'warning' },
}

let observer: IntersectionObserver | null = null

const goToUser = (userId?: number) => {
  if (userId) router.push(`/user/${userId}`)
}

const toggleComments = (item: any) => {
  const key = `${item.content_type}-${item.id}`
  activeCommentKey.value = activeCommentKey.value === key ? null : key
}

const scrollToComment = (item: any) => {
  nextTick(() => {
    const key = `${item.content_type}-${item.id}`
    const el = document.querySelector(`[data-feed-key="${key}"]`)
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
  items.value = []
  page.value = 1
  noMore.value = false
  activeCommentKey.value = null
  loadFeed()
}

const loadFeed = async (append = false) => {
  if (loading.value || loadingMore.value || noMore.value) return
  if (append) {
    loadingMore.value = true
  } else {
    loading.value = true
  }
  try {
    const apiFn = activeTab.value === 'following' ? feedApi.getFollowingFeed : feedApi.getAllFeed
    const res: any = await apiFn(page.value, pageSize)
    const newItems = res.items || []
    if (append) {
      items.value.push(...newItems)
    } else {
      items.value = newItems
    }
    if (newItems.length < pageSize) {
      noMore.value = true
    } else {
      page.value++
    }
  } catch {
    if (!append) items.value = []
  } finally {
    loading.value = false
    loadingMore.value = false
  }
}

const goToDetail = (item: any) => {
  if (item.content_type === 'blog') {
    router.push(`/blog/${item.id}`)
  } else if (item.content_type === 'news') {
    router.push(`/news/${item.id}`)
  } else if (item.content_type === 'moment') {
    router.push('/moment')
  }
}

const formatTime = (d?: string) => {
  if (!d) return ''
  const date = new Date(d)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const minutes = Math.floor(diff / 60000)
  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}小时前`
  const days = Math.floor(hours / 24)
  if (days < 30) return `${days}天前`
  return date.toLocaleDateString('zh-CN')
}

const setupInfiniteScroll = () => {
  if (!sentinelRef.value) return
  observer = new IntersectionObserver(
    (entries) => {
      if (entries[0].isIntersecting && !loadingMore.value && !noMore.value) {
        loadFeed(true)
      }
    },
    { rootMargin: '200px' },
  )
  observer.observe(sentinelRef.value)
}

onMounted(() => {
  if (!authStore.isLoggedIn) {
    activeTab.value = 'all'
  }
  loadFeed()
  setTimeout(setupInfiniteScroll, 500)
})

onUnmounted(() => {
  observer?.disconnect()
  observer = null
})
</script>

<style scoped>
.feed-view {
  max-width: 800px;
  margin: 0 auto;
  padding: 24px 16px;
}

.feed-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.feed-header h1 {
  font-size: 1.4rem;
  font-weight: 700;
  color: var(--cyber-text, var(--app-text));
  margin: 0;
}

.feed-subtitle {
  font-size: 0.8rem;
  color: var(--cyber-muted, var(--app-text-secondary));
  margin-left: 8px;
}

.feed-tabs {
  display: flex;
  gap: 4px;
  background: var(--cyber-card, var(--app-bg-card));
  border: 1px solid var(--cyber-border, var(--app-border));
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
  color: var(--cyber-muted, var(--app-text-secondary));
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s;
  font-family: inherit;
}

.tab-btn.active {
  background: var(--cyber-neon, var(--app-accent));
  color: #fff;
  box-shadow: 0 0 8px rgba(0, 212, 170, 0.3);
}

.tab-btn:not(.active):hover {
  color: var(--cyber-text, var(--app-text));
  background: var(--cyber-border, var(--app-bg-secondary));
}

.feed-content {
  min-height: 300px;
}

.feed-item {
  background: var(--cyber-card, var(--app-bg-card));
  border: 1px solid var(--cyber-border, var(--app-border));
  border-radius: 10px;
  padding: 16px;
  margin-bottom: 12px;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.feed-item:hover {
  border-color: var(--cyber-neon, var(--app-accent));
  box-shadow: 0 0 12px rgba(0, 212, 170, 0.1);
}

.feed-item-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.clickable-avatar {
  cursor: pointer;
  transition: opacity 0.2s;
}
.clickable-avatar:hover {
  opacity: 0.8;
}

.feed-item-meta {
  flex: 1;
  min-width: 0;
}

.feed-author-row {
  display: flex;
  align-items: center;
  gap: 6px;
}

.feed-author {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--cyber-text, var(--app-text));
}

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

.feed-author.clickable {
  cursor: pointer;
}
.feed-author.clickable:hover {
  color: var(--cyber-neon, var(--app-accent));
}

.feed-time {
  display: block;
  font-size: 0.72rem;
  color: var(--cyber-muted, var(--app-text-secondary));
  margin-top: 1px;
}

.feed-type-tag {
  flex-shrink: 0;
}

.feed-item-body {
  cursor: pointer;
  margin-bottom: 10px;
}

.feed-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--cyber-text, var(--app-text));
  margin: 0 0 6px;
  line-height: 1.4;
}

.feed-summary {
  font-size: 0.82rem;
  color: var(--cyber-muted, var(--app-text-secondary));
  line-height: 1.6;
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.feed-item-footer {
  display: flex;
  gap: 16px;
  padding-top: 8px;
  border-top: 1px solid var(--cyber-border, var(--app-border));
}

.feed-comments {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--cyber-border, var(--app-border));
}

.feed-sentinel {
  height: 1px;
}

.loading-more {
  padding: 16px 0;
}

.skeleton-card {
  background: var(--cyber-card, var(--app-bg-card));
  border: 1px solid var(--cyber-border, var(--app-border));
  border-radius: 10px;
  padding: 16px;
  margin-bottom: 12px;
  animation: skeleton-pulse 1.5s ease-in-out infinite;
}

.skeleton-header {
  display: flex;
  gap: 10px;
  align-items: center;
  margin-bottom: 12px;
}

.skeleton-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--cyber-border, var(--app-border));
}

.skeleton-lines {
  flex: 1;
}

.skeleton-line {
  height: 12px;
  border-radius: 4px;
  background: var(--cyber-border, var(--app-border));
  margin-bottom: 6px;
}

.skeleton-line:last-child {
  margin-bottom: 0;
}

.skeleton-body {
  padding-left: 46px;
}

.w-24 { width: 96px; }
.w-16 { width: 64px; }
.w-full { width: 100%; }
.w-3\/4 { width: 75%; }

@keyframes skeleton-pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.no-more {
  text-align: center;
  padding: 24px;
  color: var(--cyber-muted, var(--app-text-secondary));
  font-size: 0.8rem;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.empty-state p {
  color: var(--cyber-muted, var(--app-text-secondary));
  margin-bottom: 16px;
}
</style>
