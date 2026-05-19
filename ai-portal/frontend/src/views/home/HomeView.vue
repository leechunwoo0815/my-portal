<template>
  <div class="home-view">
    <HackerCanvas />
    <div class="page-content">
      <section class="hero-section">
        <div class="hero-glow hero-glow-1" />
        <div class="hero-glow hero-glow-2" />
        <div class="hero-content">
          <div class="hero-badge font-mono">>_ AI TECHNOLOGY PORTAL</div>
          <h1 class="hero-title">AI 技术门户</h1>
          <p class="hero-subtitle">专注 AI 在市政工程与智慧城市领域的落地实践</p>
          <div class="hero-actions">
            <el-button type="primary" size="large" @click="$router.push('/chat')">
              <el-icon><ChatDotRound /></el-icon>开始对话
            </el-button>
            <el-button size="large" @click="$router.push('/feed')">
              <el-icon><List /></el-icon>动态流
            </el-button>
          </div>
        </div>
      </section>

      <section class="stats-strip">
        <div class="stats-inner">
          <div class="stat-item" v-for="(s, i) in statsList" :key="i">
            <span class="stat-num font-mono">{{ s.value }}</span>
            <span class="stat-label">{{ s.label }}</span>
          </div>
        </div>
      </section>

      <section class="hot-tags-section" v-if="trendingTags.length">
        <div class="hot-tags-inner">
          <div class="hot-tags-header font-mono">
            <span class="prefix">>_</span>
            <span>热门标签</span>
          </div>
          <div class="hot-tags-list">
            <el-tag
              v-for="tag in trendingTags"
              :key="tag.name"
              size="default"
              class="hot-tag-item"
              effect="plain"
              @click="onTagClick(tag.name)"
            >
              {{ tag.name }}
              <span class="tag-count" v-if="tag.count">{{ tag.count }}</span>
            </el-tag>
          </div>
        </div>
      </section>

      <div class="content-layout">
        <div class="content-main">
          <section class="recommend-section">
            <div class="section-header">
              <h2 class="font-mono"><span class="prefix">>_</span> 推荐内容</h2>
              <div class="recommend-tabs">
                <button
                  :class="['rec-tab', { active: recTab === 'recommend' }]"
                  @click="switchRecTab('recommend')"
                >推荐</button>
                <button
                  :class="['rec-tab', { active: recTab === 'hot' }]"
                  @click="switchRecTab('hot')"
                >热门</button>
              </div>
            </div>
            <ContentCardSkeleton v-if="recLoading" :count="6" variant="grid" />
            <div v-else class="recommend-grid">
              <div
                v-for="item in recommendItems"
                :key="`${item.content_type}-${item.id}`"
                class="recommend-card"
                @click="goRecDetail(item)"
              >
                <div class="rec-card-header">
                  <el-tag size="small" :type="recTypeMap[item.content_type]?.type || 'info'" effect="plain">
                    {{ recTypeMap[item.content_type]?.label || item.content_type }}
                  </el-tag>
                  <span class="rec-score font-mono" v-if="item.score">{{ item.score.toFixed(1) }}</span>
                </div>
                <h3 class="rec-title">{{ item.title }}</h3>
                <p class="rec-summary">{{ item.summary }}</p>
                <div class="rec-footer">
                  <span class="rec-author" v-if="item.author_name">{{ item.author_name }}</span>
                  <span class="rec-stat">
                    <el-icon><View /></el-icon> {{ item.view_count || 0 }}
                  </span>
                  <span class="rec-stat">
                    <el-icon><Star /></el-icon> {{ item.likes_count || 0 }}
                  </span>
                  <span class="rec-date">{{ formatDate(item.created_at) }}</span>
                </div>
              </div>
            </div>
          </section>

          <section class="hot-ranking-section" v-if="hotRanking.length">
            <div class="section-header">
              <h2 class="font-mono"><span class="prefix">>_</span> 热门排行</h2>
            </div>
            <div class="hot-ranking-list">
              <div
                v-for="(item, idx) in hotRanking"
                :key="item.id"
                class="hot-ranking-item"
                @click="goHotDetail(item)"
              >
                <span :class="['ranking-num', `rank-${idx + 1}`]">{{ idx + 1 }}</span>
                <div class="ranking-content">
                  <h4 class="ranking-title">{{ item.title }}</h4>
                  <div class="ranking-meta">
                    <span>{{ item.author_name || '' }}</span>
                    <span><el-icon><View /></el-icon> {{ item.view_count || 0 }}</span>
                  </div>
                </div>
              </div>
            </div>
          </section>

          <section class="module-card" v-if="latestMoments.length">
            <div class="card-header">
              <h2 class="font-mono"><span class="prefix">>_</span> 社区动态</h2>
              <el-button text size="small" @click="$router.push('/moment')">更多 →</el-button>
            </div>
            <div class="moment-list">
              <div v-for="m in latestMoments" :key="m.id" class="moment-line">
                <el-avatar :size="28" :src="m.author?.avatar_url">{{ m.author?.username?.charAt(0) }}</el-avatar>
                <div class="moment-text">
                  <span class="moment-author">{{ m.author?.nickname || m.author?.username }}</span>
                  <span class="moment-content">{{ m.content?.slice(0, 100) }}{{ m.content?.length > 100 ? '...' : '' }}</span>
                </div>
              </div>
            </div>
          </section>

          <section class="module-card" v-if="latestBlog">
            <div class="card-header">
              <h2 class="font-mono"><span class="prefix">>_</span> AI 技术博客</h2>
              <router-link to="/blog">更多 →</router-link>
            </div>
            <div class="card-body" role="button" tabindex="0" @click="$router.push(`/blog/${latestBlog.id}`)" @keydown.enter="$router.push(`/blog/${latestBlog.id}`)">
              <img v-if="latestBlog.cover_image" :src="latestBlog.cover_image" :alt="latestBlog.title"
                   @error="(e) => { (e.target as HTMLImageElement).src = 'https://picsum.photos/seed/blog/600/300' }" />
              <div class="card-text">
                <el-tag size="small" class="tag-cat">{{ latestBlog.category }}</el-tag>
                <h3>{{ latestBlog.title }}</h3>
                <p>{{ latestBlog.summary || latestBlog.content?.slice(0, 100) }}…</p>
                <span class="card-date">{{ formatDate(latestBlog.created_at) }}</span>
              </div>
            </div>
            <div class="recent-list">
              <div v-for="b in recentBlogs" :key="b.id" class="recent-item" role="button" tabindex="0" @click="$router.push(`/blog/${b.id}`)" @keydown.enter="$router.push(`/blog/${b.id}`)">
                <span class="recent-title">{{ b.title }}</span>
                <span class="recent-date">{{ formatDate(b.created_at) }}</span>
              </div>
            </div>
          </section>

          <section class="module-card" v-if="latestNews">
            <div class="card-header">
              <h2 class="font-mono"><span class="prefix">>_</span> AI 新闻资讯</h2>
              <router-link to="/news">更多 →</router-link>
            </div>
            <div class="card-body" role="button" tabindex="0" @click="$router.push(`/news/${latestNews.id}`)" @keydown.enter="$router.push(`/news/${latestNews.id}`)">
              <img v-if="latestNews.cover_image" :src="latestNews.cover_image" :alt="latestNews.title"
                   @error="(e) => { (e.target as HTMLImageElement).src = 'https://picsum.photos/seed/news/600/300' }" />
              <div class="card-text">
                <el-tag size="small" class="tag-cat" type="danger">{{ latestNews.category }}</el-tag>
                <h3>{{ latestNews.title }}</h3>
                <p>{{ latestNews.summary || latestNews.content?.slice(0, 100) }}…</p>
                <span class="card-date">{{ formatDate(latestNews.created_at) }}</span>
              </div>
            </div>
            <div class="recent-list">
              <div v-for="n in recentNews" :key="n.id" class="recent-item" role="button" tabindex="0" @click="$router.push(`/news/${n.id}`)" @keydown.enter="$router.push(`/news/${n.id}`)">
                <span class="recent-title">{{ n.title }}</span>
                <span class="recent-date">{{ formatDate(n.created_at) }}</span>
              </div>
            </div>
          </section>
        </div>

        <aside class="content-sidebar">
          <section class="sidebar-card" v-if="authStore.isLoggedIn">
            <div class="sidebar-card-header">
              <h3 class="font-mono"><span class="prefix">>_</span> 每日签到</h3>
            </div>
            <div class="sidebar-checkin">
              <CheckinButton />
            </div>
          </section>

          <section class="sidebar-card" v-if="activeUsers.length">
            <div class="sidebar-card-header">
              <h3 class="font-mono"><span class="prefix">>_</span> 活跃用户</h3>
            </div>
            <div class="active-users-list">
              <div
                v-for="u in activeUsers"
                :key="u.user_id || u.id"
                class="active-user-item"
                @click="$router.push(`/user/${u.user_id || u.id}`)"
              >
                <el-avatar :size="36" :src="u.avatar_url">{{ (u.nickname || u.username || '').charAt(0) }}</el-avatar>
                <div class="active-user-info">
                  <span class="active-user-name">{{ u.nickname || u.username }}</span>
                  <span class="active-user-level" v-if="u.level_title">{{ u.level_title }}</span>
                </div>
                <el-tag size="small" type="info" effect="plain" class="active-user-points" v-if="u.total_points">
                  {{ u.total_points }} 积分
                </el-tag>
              </div>
            </div>
          </section>

          <section class="sidebar-card" v-if="authorRanking.length">
            <div class="sidebar-card-header">
              <h3 class="font-mono"><span class="prefix">>_</span> 作者排行</h3>
            </div>
            <div class="author-ranking-list">
              <div
                v-for="(u, idx) in authorRanking"
                :key="u.id || u.user_id"
                class="author-ranking-item"
                @click="$router.push(`/user/${u.id || u.user_id}`)"
              >
                <span :class="['ranking-num', `rank-${idx + 1}`]">{{ idx + 1 }}</span>
                <el-avatar :size="32" :src="u.avatar_url">{{ (u.nickname || u.username || '?')[0] }}</el-avatar>
                <div class="author-ranking-info">
                  <span class="author-ranking-name">{{ u.nickname || u.username }}</span>
                  <span class="author-ranking-points">{{ u.total_points || 0 }} 积分</span>
                </div>
              </div>
            </div>
          </section>

          <section class="sidebar-card" v-if="trendingTags.length">
            <div class="sidebar-card-header">
              <h3 class="font-mono"><span class="prefix">>_</span> 标签云</h3>
            </div>
            <div class="tag-cloud">
              <span
                v-for="(tag, idx) in trendingTags"
                :key="tag.name"
                class="tag-cloud-item"
                :class="`tag-cloud-size-${Math.min(Math.floor(idx / 3) + 1, 3)}`"
                @click="onTagClick(tag.name)"
              >
                {{ tag.name }}
              </span>
            </div>
          </section>
        </aside>
      </div>
    </div>

    <transition name="fab-fade">
      <div v-if="authStore.isLoggedIn" class="fab-write" role="button" tabindex="0" aria-label="写博客" @click="$router.push('/blog')" @keydown.enter="$router.push('/blog')" title="写博客">
        <el-icon :size="24"><EditPen /></el-icon>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ChatDotRound, List, View, Star, EditPen } from '@element-plus/icons-vue'
import { listBlogs } from '@/api/blog'
import { listNews } from '@/api/news'
import { getProjects } from '@/api/portfolio'
import { recommendApi } from '@/api/recommend'
import { useAuthStore } from '@/stores/auth'
import request from '@/api/client'
import HackerCanvas from '@/components/HackerCanvas.vue'
import CheckinButton from '@/components/checkin/CheckinButton.vue'
import { ContentCardSkeleton } from '@/components/skeleton'

const router = useRouter()
const authStore = useAuthStore()

const latestBlog = ref<any>(null)
const latestNews = ref<any>(null)
const recentBlogs = ref<any[]>([])
const recentNews = ref<any[]>([])
const latestMoments = ref<any[]>([])
const activeUsers = ref<any[]>([])
const trendingTags = ref<any[]>([])
const recommendItems = ref<any[]>([])
const recTab = ref<'recommend' | 'hot'>('recommend')
const recLoading = ref(false)
const hotRanking = ref<any[]>([])
const authorRanking = ref<any[]>([])

const stats = ref({ blog: 0, project: 0, news: 0, solution: 0, product: 0 })
const statsList = ref([
  { label: '技术博客', value: 0 },
  { label: '项目案例', value: 0 },
  { label: '新闻资讯', value: 0 },
  { label: '解决方案', value: 0 },
  { label: 'AI 产品', value: 0 },
])

const recTypeMap: Record<string, { label: string; type: '' | 'primary' | 'success' | 'warning' | 'danger' | 'info' }> = {
  blog: { label: '博客', type: 'primary' },
  news: { label: '资讯', type: 'warning' },
  product: { label: '产品', type: 'success' },
  solution: { label: '方案', type: 'info' },
}

let scrollObserver: IntersectionObserver | null = null
let statsObservers: IntersectionObserver[] = []
let statsTimers: ReturnType<typeof setInterval>[] = []
let visibilityTimeout: ReturnType<typeof setTimeout> | null = null

const onTagClick = (tagName: string) => {
  router.push({ path: '/blog', query: { tag: tagName } })
}

const switchRecTab = (tab: 'recommend' | 'hot') => {
  if (tab === recTab.value) return
  recTab.value = tab
  loadRecommend()
}

const loadRecommend = async () => {
  recLoading.value = true
  try {
    const apiFn = recTab.value === 'recommend' ? recommendApi.getFeed : recommendApi.getHot
    const res: any = await apiFn(1, 8)
    recommendItems.value = res.items || []
  } catch {
    recommendItems.value = []
  } finally {
    recLoading.value = false
  }
}

const goRecDetail = (item: any) => {
  const pathMap: Record<string, string> = {
    blog: '/blog',
    news: '/news',
    product: '/products',
    solution: '/solutions',
  }
  const basePath = pathMap[item.content_type] || '/blog'
  router.push(`${basePath}/${item.id}`)
}

const goHotDetail = (item: any) => {
  const pathMap: Record<string, string> = { blog: '/blog', news: '/news', product: '/products', solution: '/solutions' }
  const basePath = pathMap[item.content_type] || '/blog'
  router.push(`${basePath}/${item.id}`)
}

const fetchAll = async () => {
  try {
    const [b, n, pr, mo] = await Promise.allSettled([
      listBlogs({ page: 1, page_size: 5 }),
      listNews({ page: 1, page_size: 5 }),
      getProjects({ page: 1, page_size: 3 }),
      request.get('/v1/moment/', { params: { page: 1, page_size: 5 } }),
    ])

    if (b.status === 'fulfilled') {
      const d = b.value as any
      const items: any[] = d?.items || []
      latestBlog.value = items[0] || null
      recentBlogs.value = items.slice(1, 5)
      stats.value.blog = d?.total || items.length
      statsList.value[0].value = stats.value.blog
    }
    if (n.status === 'fulfilled') {
      const d = n.value as any
      const items: any[] = Array.isArray(d) ? d : (d?.items || [])
      latestNews.value = items[0] || null
      recentNews.value = items.slice(1, 5)
      stats.value.news = items.length
      statsList.value[2].value = stats.value.news
    }
    if (pr.status === 'fulfilled') {
      const d = pr.value as any
      stats.value.project = d?.total || 0
      statsList.value[1].value = stats.value.project
    }
    if (mo.status === 'fulfilled') {
      const d = mo.value as any
      latestMoments.value = d?.items || []
    }
  } catch (_) {}

  try {
    const res = await request.get('/v1/user/active', { params: { limit: 6 } })
    const d = res.data || res
    activeUsers.value = Array.isArray(d) ? d : (d?.items || [])
  } catch (_) {
    const seen = new Map<number, any>()
    for (const m of latestMoments.value) {
      if (m.author && !seen.has(m.author.id || m.author.user_id)) {
        seen.set(m.author.id || m.author.user_id, m.author)
      }
      if (seen.size >= 6) break
    }
    activeUsers.value = Array.from(seen.values())
  }

  try {
    const res: any = await recommendApi.getTrendingTags(20)
    trendingTags.value = res.tags || []
  } catch {}

  try {
    const res: any = await recommendApi.getHot(1, 10)
    hotRanking.value = res?.items || []
  } catch {}

  try {
    const res = await request.get('/v1/user/active', { params: { limit: 10 } })
    const d = res.data || res
    authorRanking.value = Array.isArray(d) ? d : (d?.items || [])
  } catch {}

  loadRecommend()
}

const formatDate = (d?: string) => {
  if (!d) return ''
  return new Date(d).toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' }).replace(/\//g, '-')
}

onMounted(async () => {
  await fetchAll()
  nextTick(() => {
    setupScrollAnimations()
    visibilityTimeout = setTimeout(() => {
      document.querySelectorAll('.module-card, .recommend-section, .stats-strip, .hot-tags-section, .sidebar-card').forEach(el => {
        el.classList.add('visible')
      })
    }, 3000)
  })
  setupStatsCounter()
})

onUnmounted(() => {
  scrollObserver?.disconnect()
  scrollObserver = null
  statsObservers.forEach(obs => obs.disconnect())
  statsObservers = []
  statsTimers.forEach(timer => clearInterval(timer))
  statsTimers = []
  if (visibilityTimeout !== null) {
    clearTimeout(visibilityTimeout)
    visibilityTimeout = null
  }
})

const setupScrollAnimations = () => {
  const els = document.querySelectorAll('.stats-strip, .recommend-section, .module-card, .hot-tags-section, .sidebar-card')
  scrollObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible')
          scrollObserver?.unobserve(entry.target)
        }
      })
    },
    { threshold: 0.1 }
  )
  els.forEach((el, i) => {
    ;(el as HTMLElement).style.transitionDelay = `${i % 4 * 0.08}s`
    scrollObserver!.observe(el)
  })
}

const setupStatsCounter = () => {
  const nums = document.querySelectorAll('.stat-num')
  nums.forEach((el) => {
    const target = parseInt(el.textContent || '0', 10)
    if (target === 0) return
    const obs = new IntersectionObserver((entries) => {
      if (entries[0].isIntersecting) {
        let cur = 0
        const step = Math.ceil(target / 30)
        const timer = setInterval(() => {
          cur = Math.min(cur + step, target)
          el.textContent = String(cur)
          if (cur >= target) clearInterval(timer)
        }, 40)
        statsTimers.push(timer)
        obs.disconnect()
      }
    }, { threshold: 0.5 })
    statsObservers.push(obs)
    obs.observe(el)
  })
}
</script>

<style scoped>
.home-view {
  min-height: 100vh;
  background: var(--cyber-bg, var(--app-bg));
  position: relative;
  overflow-x: hidden;
}
.page-content { position: relative; z-index: 1; }

.hero-section {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 420px;
  padding: 64px 24px;
  background: linear-gradient(180deg, rgba(0,212,170,0.04) 0%, transparent 100%);
  position: relative;
  overflow: hidden;
}
.hero-glow {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  pointer-events: none;
}
.hero-glow-1 {
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, rgba(0,212,170,0.12) 0%, transparent 70%);
  top: -100px;
  right: 10%;
  animation: glowPulse 4s ease-in-out infinite;
}
.hero-glow-2 {
  width: 300px;
  height: 300px;
  background: radial-gradient(circle, rgba(240,180,41,0.08) 0%, transparent 70%);
  bottom: 0;
  left: 5%;
  animation: glowPulse 5s ease-in-out infinite 1s;
}
@keyframes glowPulse {
  0%, 100% { opacity: 0.6; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.1); }
}
.hero-content { text-align: center; max-width: 640px; position: relative; z-index: 1; }
.hero-badge {
  display: inline-block;
  font-size: 0.7rem;
  letter-spacing: 3px;
  color: var(--cyber-neon, var(--app-accent));
  border: 1px solid var(--cyber-neon, var(--app-accent));
  padding: 4px 12px;
  border-radius: 20px;
  margin-bottom: 20px;
  opacity: 0.8;
}
.hero-title {
  font-size: 2.6rem;
  font-weight: 800;
  color: var(--cyber-text, var(--app-text));
  margin: 0 0 12px;
  letter-spacing: -0.5px;
}
.hero-subtitle {
  font-size: 1rem;
  color: var(--cyber-muted, var(--app-text-secondary));
  margin-bottom: 32px;
}
.hero-actions { display: flex; gap: 16px; justify-content: center; }

.stats-strip {
  background: var(--cyber-card, var(--app-bg-card));
  border-top: 1px solid var(--cyber-border, var(--app-border));
  border-bottom: 1px solid var(--cyber-border, var(--app-border));
}
.stats-inner {
  max-width: 900px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px 24px;
  gap: 8px;
}
.stat-item { display: flex; flex-direction: column; align-items: center; flex: 1; }
.stat-num { font-size: 1.6rem; font-weight: 700; color: var(--cyber-neon, var(--app-accent)); }
.stat-label { font-size: 0.75rem; color: var(--cyber-muted, var(--app-text-secondary)); margin-top: 2px; }

.hot-tags-section {
  background: var(--cyber-card, var(--app-bg-card));
  border-bottom: 1px solid var(--cyber-border, var(--app-border));
}
.hot-tags-inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 16px 24px;
  display: flex;
  align-items: center;
  gap: 16px;
}
.hot-tags-header {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--cyber-text, var(--app-text));
  flex-shrink: 0;
}
.hot-tags-header .prefix { color: var(--cyber-neon, var(--app-accent)); }
.hot-tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  flex: 1;
}
.hot-tag-item {
  cursor: pointer;
  transition: transform 0.15s, box-shadow 0.15s;
}
.hot-tag-item:hover {
  transform: translateY(-1px);
  box-shadow: 0 0 8px rgba(0,212,170,0.2);
}
.tag-count {
  margin-left: 4px;
  font-size: 0.7rem;
  opacity: 0.6;
}

.content-layout {
  max-width: 1200px;
  margin: 48px auto 64px;
  padding: 0 24px;
  display: grid;
  grid-template-columns: 3fr 1fr;
  gap: 24px;
}
.content-main {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.content-sidebar {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.sidebar-card {
  background: var(--cyber-card, var(--app-bg-card));
  border: 1px solid var(--cyber-border, var(--app-border));
  border-radius: 8px;
  overflow: hidden;
}
.sidebar-card-header {
  padding: 14px 16px;
  border-bottom: 1px solid var(--cyber-border, var(--app-border));
}
.sidebar-card-header h3 {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--cyber-text, var(--app-text));
  display: flex;
  align-items: center;
  gap: 6px;
  margin: 0;
}
.sidebar-card-header .prefix { color: var(--cyber-neon, var(--app-accent)); }
.sidebar-checkin { padding: 16px; display: flex; justify-content: center; }

.recommend-section {
  background: var(--cyber-card, var(--app-bg-card));
  border: 1px solid var(--cyber-border, var(--app-border));
  border-radius: 8px;
  padding: 16px;
}
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.section-header h2 {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--cyber-text, var(--app-text));
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
}
.section-header .prefix { color: var(--cyber-neon, var(--app-accent)); }
.recommend-tabs {
  display: flex;
  gap: 4px;
  background: var(--cyber-bg, var(--app-bg));
  border: 1px solid var(--cyber-border, var(--app-border));
  border-radius: 6px;
  padding: 2px;
}
.rec-tab {
  padding: 4px 14px;
  border: none;
  border-radius: 4px;
  background: transparent;
  color: var(--cyber-muted, var(--app-text-secondary));
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.2s;
  font-family: inherit;
}
.rec-tab.active {
  background: var(--cyber-neon, var(--app-accent));
  color: #fff;
}
.recommend-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  min-height: 120px;
}
.recommend-card {
  background: var(--cyber-bg, var(--app-bg));
  border: 1px solid var(--cyber-border, var(--app-border));
  border-radius: 8px;
  padding: 12px;
  cursor: pointer;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.recommend-card:hover {
  border-color: var(--cyber-neon, var(--app-accent));
  box-shadow: 0 0 12px rgba(0,212,170,0.1);
}
.rec-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.rec-score {
  font-size: 0.75rem;
  color: var(--cyber-amber, #f0b429);
  font-weight: 600;
}
.rec-title {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--cyber-text, var(--app-text));
  margin: 0 0 4px;
  line-height: 1.3;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.rec-summary {
  font-size: 0.78rem;
  color: var(--cyber-muted, var(--app-text-secondary));
  line-height: 1.5;
  margin: 0 0 8px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.rec-footer {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 0.72rem;
  color: var(--cyber-muted, var(--app-text-secondary));
}
.rec-author { font-weight: 500; }
.rec-stat { display: flex; align-items: center; gap: 2px; }
.rec-date { margin-left: auto; }

.active-users-list { padding: 12px 16px; }
.active-user-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 0;
  border-bottom: 1px solid var(--cyber-border, var(--app-border));
  cursor: pointer;
  transition: background 0.15s;
}
.active-user-item:last-child { border-bottom: none; }
.active-user-item:hover { background: var(--cyber-bg, var(--app-bg-secondary)); margin: 0 -16px; padding: 8px 16px; }
.active-user-info { flex: 1; min-width: 0; }
.active-user-name {
  display: block;
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--cyber-text, var(--app-text));
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.active-user-level {
  display: block;
  font-size: 0.7rem;
  color: var(--cyber-muted, var(--app-text-secondary));
  margin-top: 1px;
}
.active-user-points { flex-shrink: 0; }

.tag-cloud {
  padding: 16px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
  justify-content: center;
}
.tag-cloud-item {
  cursor: pointer;
  color: var(--cyber-muted, var(--app-text-secondary));
  transition: color 0.15s, transform 0.15s;
  white-space: nowrap;
}
.tag-cloud-item:hover {
  color: var(--cyber-neon, var(--app-accent));
  transform: scale(1.08);
}
.tag-cloud-size-1 { font-size: 0.85rem; font-weight: 600; }
.tag-cloud-size-2 { font-size: 0.75rem; font-weight: 500; }
.tag-cloud-size-3 { font-size: 0.68rem; font-weight: 400; }

.hot-ranking-section {
  background: var(--cyber-card, var(--app-bg-card));
  border: 1px solid var(--cyber-border, var(--app-border));
  border-radius: 8px;
  overflow: hidden;
}
.hot-ranking-list { padding: 0 16px; }
.hot-ranking-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 0;
  border-bottom: 1px solid var(--cyber-border, var(--app-border));
  cursor: pointer;
  transition: background 0.15s;
}
.hot-ranking-item:last-child { border-bottom: none; }
.hot-ranking-item:hover { background: var(--cyber-neon-light); margin: 0 -16px; padding: 10px 16px; }
.ranking-num {
  width: 22px;
  height: 22px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
  font-family: 'JetBrains Mono', monospace;
  background: var(--cyber-border, var(--app-border));
  color: var(--app-text-secondary);
  flex-shrink: 0;
}
.rank-1 { background: var(--cyber-neon, #00d4aa); color: #fff; }
.rank-2 { background: var(--cyber-amber, #f0b429); color: #fff; }
.rank-3 { background: #e6a23c; color: #fff; }
.ranking-content { flex: 1; min-width: 0; }
.ranking-title {
  font-size: 13px;
  font-weight: 500;
  color: var(--app-text);
  margin: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.ranking-meta {
  display: flex;
  gap: 10px;
  font-size: 11px;
  color: var(--app-text-secondary);
  margin-top: 2px;
}
.ranking-meta .el-icon { margin-right: 2px; }

.author-ranking-list { padding: 8px 16px; }
.author-ranking-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 0;
  border-bottom: 1px solid var(--cyber-border, var(--app-border));
  cursor: pointer;
  transition: background 0.15s;
}
.author-ranking-item:last-child { border-bottom: none; }
.author-ranking-item:hover { background: var(--cyber-neon-light); margin: 0 -16px; padding: 8px 16px; }
.author-ranking-info { flex: 1; min-width: 0; }
.author-ranking-name {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: var(--app-text);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.author-ranking-points {
  font-size: 11px;
  color: var(--cyber-amber, #f0b429);
}

.module-card {
  background: var(--cyber-card, var(--app-bg-card));
  border: 1px solid var(--cyber-border, var(--app-border));
  border-radius: 8px;
  overflow: hidden;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 16px;
  border-bottom: 1px solid var(--cyber-border, var(--app-border));
}
.card-header h2 { font-size: 0.95rem; font-weight: 600; color: var(--cyber-text, var(--app-text)); display: flex; align-items: center; gap: 8px; margin: 0; }
.card-header .prefix { color: var(--cyber-neon, var(--app-accent)); }
.card-header a { font-size: 0.75rem; color: var(--cyber-neon, var(--app-accent)); }

.card-body { display: flex; gap: 12px; padding: 12px 16px; cursor: pointer; }
.card-body img { width: 100px; height: 70px; object-fit: cover; border-radius: 6px; flex-shrink: 0; }
.card-text { flex: 1; min-width: 0; }
.tag-cat { margin-bottom: 6px; }
.card-text h3 { font-size: 0.9rem; font-weight: 600; color: var(--cyber-text, var(--app-text)); margin: 0 0 4px; line-height: 1.3; }
.card-text p { font-size: 0.78rem; color: var(--cyber-muted, var(--app-text-secondary)); line-height: 1.5; margin: 0 0 6px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.card-date { font-size: 0.7rem; color: var(--cyber-muted, var(--app-text-secondary)); }

.recent-list { padding: 0 16px 12px; }
.recent-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid var(--cyber-border, var(--app-border));
  cursor: pointer;
}
.recent-item:last-child { border-bottom: none; }
.recent-title { font-size: 0.8rem; color: var(--cyber-text, var(--app-text)); flex: 1; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.recent-date { font-size: 0.7rem; color: var(--cyber-muted, var(--app-text-secondary)); flex-shrink: 0; margin-left: 8px; }
.recent-item:hover .recent-title { color: var(--cyber-neon, var(--app-accent)); }

.moment-list { padding: 8px 16px 12px; }
.moment-line { display: flex; gap: 8px; align-items: flex-start; padding: 8px 0; border-bottom: 1px solid var(--cyber-border, var(--app-border)); }
.moment-line:last-child { border-bottom: none; }
.moment-text { flex: 1; min-width: 0; }
.moment-author { font-size: 0.8rem; font-weight: 600; color: var(--cyber-text, var(--app-text)); margin-right: 6px; }
.moment-content { font-size: 0.8rem; color: var(--cyber-muted, var(--app-text-secondary)); word-break: break-word; }

.fab-write {
  position: fixed;
  right: 32px;
  bottom: 32px;
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background: var(--cyber-neon, var(--app-accent));
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 0 16px rgba(0,212,170,0.35);
  transition: transform 0.2s, box-shadow 0.2s;
  z-index: 100;
}
.fab-write:hover {
  transform: scale(1.1);
  box-shadow: 0 0 24px rgba(0,212,170,0.45);
}
.fab-fade-enter-active { transition: opacity 0.3s, transform 0.3s; }
.fab-fade-leave-active { transition: opacity 0.2s, transform 0.2s; }
.fab-fade-enter-from { opacity: 0; transform: scale(0.6); }
.fab-fade-leave-to { opacity: 0; transform: scale(0.6); }

@media (max-width: 900px) {
  .content-layout { grid-template-columns: 1fr; }
  .content-sidebar { flex-direction: row; flex-wrap: wrap; }
  .sidebar-card { flex: 1; min-width: 280px; }
  .hot-tags-inner { flex-direction: column; align-items: flex-start; }
  .recommend-grid { grid-template-columns: 1fr; }
}
@media (max-width: 600px) {
  .hero-title { font-size: 1.8rem; }
  .stats-inner { flex-wrap: wrap; gap: 12px; }
  .content-sidebar { flex-direction: column; }
  .sidebar-card { min-width: unset; }
  .fab-write { right: 20px; bottom: 20px; }
}
</style>
