<!-- 新闻详情 - 使用 markdown-it 渲染，支持上/下条导航 -->
<template>
  <div class="news-detail-view">
    <div class="reading-progress" :style="{ width: progress + '%' }" />
    <div class="back-link">
      <el-button text @click="router.push('/news')">
        <el-icon><ArrowLeft /></el-icon>返回新闻列表
      </el-button>
    </div>

    <DetailSkeleton v-if="loading" />

    <article v-else-if="item" class="news-article">
      <header class="article-header">
        <el-tag v-if="item.category" size="small" type="danger">{{ item.category }}</el-tag>
        <h1 class="article-title">{{ item.title }}</h1>
        <div class="article-author" v-if="item.author">
          <router-link :to="`/user/${item.author.id}`" class="author-link" :aria-label="item.author.nickname || item.author.username">
            <el-avatar :size="36" :src="item.author.avatar_url">{{ item.author.nickname?.[0] || item.author.username?.[0] }}</el-avatar>
          </router-link>
          <div class="author-info">
            <router-link :to="`/user/${item.author.id}`" class="author-link">
              <span class="author-name">{{ item.author.nickname || item.author.username }}</span>
            </router-link>
            <el-tag size="small" :type="item.author.level === 999 ? 'success' : 'warning'">
              {{ item.author.level === 999 ? '管理员' : 'LV' + item.author.level }}
            </el-tag>
          </div>
        </div>
        <div class="article-meta">
          <span>{{ formatDate(item.created_at) }}</span>
          <span v-if="item.view_count">{{ item.view_count }} 次浏览</span>
        </div>
        <div class="article-tags" v-if="item.tags">
          <el-tag v-for="tag in item.tags.split(',')" :key="tag" size="small" effect="plain">{{ tag.trim() }}</el-tag>
        </div>
      </header>
      <div v-if="item.cover_image" class="article-cover">
        <img :src="item.cover_image" :alt="item.title" loading="lazy" @error="(e: Event) => ((e.target as HTMLElement).style.display='none')" />
      </div>
      <div class="article-summary" v-if="item.summary">
        <p>{{ item.summary }}</p>
      </div>
      <div class="article-content markdown-body" v-html="rendered"></div>
      <nav class="article-nav">
        <div class="nav-prev">
          <el-button v-if="prevItem" text @click="goTo(prevItem.id)">← {{ prevItem.title }}</el-button>
        </div>
        <div class="nav-next">
          <el-button v-if="nextItem" text @click="goTo(nextItem.id)">{{ nextItem.title }} →</el-button>
        </div>
      </nav>
      <CommentSection v-if="item" targetType="news" :targetId="item.id" :authorId="item.author?.id || item.author_id" />
    </article>

    <div v-else class="state-box" style="color:red">❌ 数据加载失败</div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ArrowLeft } from '@element-plus/icons-vue'
import { getNewsById, listNews } from '@/api/news'
import CommentSection from '@/components/CommentSection.vue'
import { DetailSkeleton } from '@/components/skeleton'
import { useMarkdown } from '@/composables/useMarkdown'
import { useReadingProgress } from '@/composables/useReadingProgress'

const { renderMd } = useMarkdown()
const { progress } = useReadingProgress()

const router = useRouter()
const route = useRoute()
const loading = ref(true)
const item = ref<any>(null)
const prevItem = ref<any>(null)
const nextItem = ref<any>(null)
const allItems = ref<any[]>([])

const rendered = computed(() => item.value?.content ? renderMd(item.value.content) : '')

const goTo = (id: number) => {
  // 使用 router.push 触发路由变化，watch 会自动加载数据
  router.push(`/news/${id}`)
}

const formatDate = (d?: string) => d ? new Date(d).toLocaleString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false }).replace(/\//g, '-') : ''

// 加载所有列表数据（用于上下条导航）
const fetchAllItems = async () => {
  if (allItems.value.length > 0) return allItems.value
  try {
    const res: any = await listNews()
    allItems.value = Array.isArray(res) ? res : (res?.items || [])
  } catch {
    allItems.value = []
  }
  return allItems.value
}

// 加载当前新闻详情 + 导航信息
const loadNews = async (newsId: number) => {
  if (!newsId) return

  loading.value = true
  prevItem.value = null
  nextItem.value = null

  try {
    // 并行加载详情和列表
    const [detail, items] = await Promise.all([
      getNewsById(newsId),
      fetchAllItems()
    ])
    // @ts-ignore
    item.value = detail

    // 计算上下条
    const idx = items.findIndex((b: any) => Number(b.id) === newsId)
    if (idx > 0) prevItem.value = items[idx - 1]
    if (idx < items.length - 1) nextItem.value = items[idx + 1]
  } catch (e: any) {
    console.error('News load error:', e)
    item.value = null
  } finally {
    loading.value = false
  }
}

// 核心：监听路由变化重新加载数据
watch(() => route.params.id, (newId) => {
  if (newId) {
    loadNews(Number(newId))
  }
}, { immediate: true })
</script>

<style scoped>
.news-detail-view {
  min-height: calc(100vh - 60px);
  background: var(--app-bg, #f5f7fa);
  padding: 32px 0;
}
.reading-progress {
  position: fixed;
  top: 56px;
  left: 0;
  height: 3px;
  background: var(--cyber-neon, #00d4aa);
  box-shadow: 0 0 8px var(--cyber-neon, #00d4aa);
  z-index: 99;
  transition: width 0.1s linear;
}
.back-link { max-width: 800px; margin: 0 auto 24px; padding: 0 20px; }
.state-box { text-align: center; padding: 80px 20px; font-size: 18px; color: #909399; }
.news-article {
  max-width: 800px; margin: 0 auto;
  background: var(--app-bg-card, #fff);
  border: 1px solid var(--app-border, #eee);
  border-radius: 12px; padding: 40px;
}
.article-header { margin-bottom: 24px; }
.article-title { font-size: 1.8rem; font-weight: 700; margin: 12px 0 8px; color: var(--app-text); }
.article-author { display: flex; align-items: center; gap: 12px; margin: 12px 0; padding: 12px 0; }
.author-info { display: flex; align-items: center; gap: 8px; }
.author-name { font-weight: 500; color: var(--app-text); }
.author-link { text-decoration: none; color: inherit; }
.author-link:hover .author-name { color: var(--cyber-neon, #00d4aa); }
.article-meta { color: var(--app-text-secondary); font-size: 0.85rem; display: flex; gap: 16px; }
.article-tags { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px; }
.article-cover { margin: -40px -40px 24px; border-radius: 12px 12px 0 0; overflow: hidden; }
.article-cover img { width: 100%; max-height: 400px; object-fit: cover; display: block; }
.article-summary { margin-bottom: 20px; padding: 16px; background: var(--app-bg-secondary); border-radius: 8px; color: var(--app-text-secondary); }
.article-content { line-height: 1.8; color: var(--app-text); font-size: 1rem; }
.article-nav {
  display: flex; justify-content: space-between;
  margin-top: 40px; padding-top: 20px;
  border-top: 1px solid var(--app-border);
}
.nav-prev, .nav-next { max-width: 45%; }
.nav-prev .el-button, .nav-next .el-button { text-align: left; white-space: normal; height: auto; line-height: 1.4; }

@media (max-width: 768px) {
  .news-detail-view { padding: 16px 0; }
  .news-article { padding: 20px; }
  .article-cover { margin: -20px -20px 16px; }
  .article-title { font-size: 1.4rem; }
  .back-link { padding: 0 16px; }
}
</style>
