<!-- 博客详情 - 增强版：进度条 + TOC + 阅读时间 + 作者卡片 + 相关推荐 -->
<template>
  <div class="blog-detail-view">
    <!-- 阅读进度条 -->
    <div class="reading-progress" :style="{ width: progress + '%' }" />

    <div class="back-link">
      <el-button text @click="router.push('/blog')">
        <el-icon><ArrowLeft /></el-icon>返回博客列表
      </el-button>
    </div>

    <DetailSkeleton v-if="loading" />

    <template v-else-if="blog">
      <div class="article-layout">
        <article class="blog-article">
          <header class="article-header">
            <el-tag v-if="blog.category" size="small">{{ blog.category }}</el-tag>
            <h1 class="article-title">{{ blog.title }}</h1>
            <div class="article-author" v-if="blog.author">
              <router-link :to="`/user/${blog.author.id}`" class="author-link" :aria-label="blog.author.nickname || blog.author.username">
                <el-avatar :size="36" :src="blog.author.avatar_url">{{ blog.author.nickname?.[0] || blog.author.username?.[0] }}</el-avatar>
              </router-link>
              <div class="author-info">
                <router-link :to="`/user/${blog.author.id}`" class="author-link">
                  <span class="author-name">{{ blog.author.nickname || blog.author.username }}</span>
                </router-link>
                <el-tag size="small" :type="blog.author.level === 999 ? 'success' : 'warning'">
                  {{ blog.author.level === 999 ? '管理员' : 'LV' + blog.author.level }}
                </el-tag>
              </div>
            </div>
            <div class="article-meta">
              <span>{{ formatDate(blog.created_at) }}</span>
              <span v-if="blog.view_count">{{ blog.view_count }} 次浏览</span>
              <span>📖 约 {{ readingTime }} 分钟阅读</span>
            </div>
            <div class="article-tags" v-if="blog.tags">
              <el-tag v-for="tag in blog.tags.split(',')" :key="tag" size="small" effect="plain">{{ tag.trim() }}</el-tag>
            </div>
            <div class="article-actions">
              <LikeButton target-type="blog" :target-id="blog.id" :count="blog.likes_count" />
              <FavoriteButton target-type="blog" :target-id="blog.id" />
              <ShareButton :url="currentUrl" :title="blog.title" />
              <el-button size="small" @click="exportMarkdown">
                <el-icon><Download /></el-icon> 导出MD
              </el-button>
              <el-button size="small" v-if="isAuthor" type="primary" @click="editBlog">编辑</el-button>
            </div>
          </header>
          <div v-if="blog.cover_image" class="article-cover">
            <img :src="blog.cover_image" :alt="blog.title" loading="lazy" @error="(e) => { (e.target as HTMLImageElement).style.display = 'none' }" />
          </div>
          <div ref="articleContentRef" class="article-content markdown-body" v-html="rendered" />

          <!-- 作者卡片 -->
          <div v-if="blog.author" class="author-card">
            <div class="author-card-main">
              <router-link :to="`/user/${blog.author.id}`" class="author-card-avatar">
                <el-avatar :size="56" :src="blog.author.avatar_url">{{ blog.author.nickname?.[0] || blog.author.username?.[0] }}</el-avatar>
              </router-link>
              <div class="author-card-info">
                <router-link :to="`/user/${blog.author.id}`" class="author-card-name">
                  {{ blog.author.nickname || blog.author.username }}
                </router-link>
                <p class="author-card-bio">{{ blog.author.bio || '这个人很懒，什么都没写' }}</p>
                <div class="author-card-stats">
                  <span>文章 {{ blog.author.blog_count || 0 }}</span>
                  <span>粉丝 {{ blog.author.followers_count || 0 }}</span>
                  <span>获赞 {{ blog.author.total_likes || 0 }}</span>
                </div>
              </div>
              <div class="author-card-actions" v-if="!isAuthor && authStore.isLoggedIn">
                <FollowButton :user-id="blog.author.id" />
              </div>
            </div>
          </div>

          <!-- 相关推荐 -->
          <div v-if="relatedArticles.length" class="related-section">
            <h3 class="related-title">相关推荐</h3>
            <div class="related-grid">
              <div v-for="item in relatedArticles" :key="item.id" class="related-card" @click="router.push(`/blog/${item.id}`)">
                <h4 class="related-card-title">{{ item.title }}</h4>
                <p class="related-card-summary">{{ item.summary || '' }}</p>
                <div class="related-card-meta">
                  <span>{{ item.author_name || '' }}</span>
                  <span>{{ item.view_count || 0 }} 阅读</span>
                </div>
              </div>
            </div>
          </div>

          <nav class="article-nav">
            <el-button v-if="prevBlog" text @click="goTo(prevBlog.id)">← {{ prevBlog.title }}</el-button>
            <el-button v-if="nextBlog" text @click="goTo(nextBlog.id)">{{ nextBlog.title }} →</el-button>
          </nav>
          <CommentSection v-if="blog" targetType="blog" :targetId="blog.id" :authorId="blog.author?.id || blog.author_id" />
        </article>

        <!-- TOC 侧边栏 -->
        <aside class="toc-sidebar" v-if="tocItems.length">
          <div class="toc-header">目录</div>
          <nav class="toc-nav">
            <TocNode v-for="item in tocItems" :key="item.id" :item="item" :active-id="activeTocId" />
          </nav>
        </aside>
      </div>
    </template>

    <div v-else class="state-box" style="color:red">❌ 博客数据加载失败</div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ArrowLeft, Download } from '@element-plus/icons-vue'
import { getBlogById, listBlogs } from '@/api/blog'
import CommentSection from '@/components/CommentSection.vue'
import { DetailSkeleton } from '@/components/skeleton'
import { useMarkdown } from '@/composables/useMarkdown'
import { useReadingProgress } from '@/composables/useReadingProgress'
import { useToc } from '@/composables/useToc'
import { toggleLike as apiToggleLike, toggleFavorite as apiToggleFavorite, checkLiked, checkFavorited } from '@/api/interaction'
import { recommendApi } from '@/api/recommend'
import { historyApi } from '@/api/history'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import LikeButton from '@/components/interaction/LikeButton.vue'
import FavoriteButton from '@/components/interaction/FavoriteButton.vue'
import ShareButton from '@/components/interaction/ShareButton.vue'
import FollowButton from '@/components/interaction/FollowButton.vue'
import TocNode from './TocNode.vue'

const { renderMd } = useMarkdown()
const { progress } = useReadingProgress()
const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const loading = ref(true)
const blog = ref<any>(null)
const prevBlog = ref<any>(null)
const nextBlog = ref<any>(null)
const liked = ref(false)
const favorited = ref(false)
const likesCount = ref(0)
const likeLoading = ref(false)
const favoriteLoading = ref(false)
const relatedArticles = ref<any[]>([])
const activeTocId = ref('')
const articleContentRef = ref<HTMLElement>()
let tocObserver: IntersectionObserver | null = null

const rendered = computed(() => blog.value?.content ? renderMd(blog.value.content) : '')
const { toc: tocItems } = useToc(() => rendered.value)
const readingTime = computed(() => Math.ceil((blog.value?.content?.length || 0) / 500))
const currentUrl = computed(() => window.location.href)

const isAuthor = computed(() => {
  return authStore.user && blog.value && authStore.user.id === (blog.value.author?.id || blog.value.author_id)
})

const goTo = (id: number) => router.push(`/blog/${id}`)
const editBlog = () => router.push({ path: '/admin/blogs', query: { edit: String(blog.value?.id) } })

const exportMarkdown = () => {
  if (!blog.value) return
  const title = blog.value.title || '未命名'
  const content = blog.value.content || ''
  const md = `# ${title}\n\n${content}`
  const blob = new Blob([md], { type: 'text/markdown;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${title.replace(/[/\\?%*:|"<>]/g, '-')}.md`
  a.click()
  URL.revokeObjectURL(url)
}
const formatDate = (d?: string) => d ? new Date(d).toLocaleString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false }).replace(/\//g, '-') : ''

const fetchNavigation = async (currentId: number) => {
  try {
    const res: any = await listBlogs({ page: 1, page_size: 100 })
    const items: any[] = res?.items || []
    const idx = items.findIndex((b: any) => Number(b.id) === currentId)
    if (idx > 0) prevBlog.value = items[idx - 1]
    if (idx < items.length - 1) nextBlog.value = items[idx + 1]
  } catch (_) { console.error(_) }
}

const fetchRelated = async (id: number) => {
  try {
    const res: any = await recommendApi.getRelated('blog', id, 4)
    relatedArticles.value = res?.items || res || []
  } catch { relatedArticles.value = [] }
}

const loadBlog = async (id: number) => {
  if (!id) return
  loading.value = true
  try {
    const res = await getBlogById(id)
    blog.value = res.data || res
    likesCount.value = blog.value?.likes_count || 0
    await Promise.all([fetchNavigation(id), fetchRelated(id)])
    if (authStore.isLoggedIn) {
      historyApi.record('blog', id).catch(() => {})
      try {
        const [ls, fs]: any[] = await Promise.all([
          checkLiked('blog', id),
          checkFavorited('blog', id),
        ])
        liked.value = ls?.liked ?? ls?.is_liked
        favorited.value = fs?.favorited ?? fs?.is_favorited
      } catch (e) { console.error(e) }
    }
  } catch (e: any) {
    console.error('Blog load error:', e)
    blog.value = null
  } finally {
    loading.value = false
  }
}

const setupTocObserver = () => {
  nextTick(() => {
    tocObserver?.disconnect()
    if (!articleContentRef.value) return
    const headings = articleContentRef.value.querySelectorAll('h1[id], h2[id], h3[id], h4[id]')
    if (!headings.length) return
    tocObserver = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            activeTocId.value = (entry.target as HTMLElement).id
          }
        }
      },
      { rootMargin: '-80px 0px -70% 0px' }
    )
    headings.forEach(h => tocObserver!.observe(h))
  })
}

const toggleLike = async () => {
  if (!authStore.isLoggedIn || !blog.value || likeLoading.value) return
  likeLoading.value = true
  try {
    const res: any = await apiToggleLike({ target_type: 'blog', target_id: blog.value.id })
    liked.value = res?.liked ?? res?.is_liked
    likesCount.value = res?.likes_count
  } catch (e) { console.error(e); ElMessage.error('操作失败') } finally {
    likeLoading.value = false
  }
}

const toggleFavorite = async () => {
  if (!authStore.isLoggedIn || !blog.value || favoriteLoading.value) return
  favoriteLoading.value = true
  try {
    const res: any = await apiToggleFavorite({ target_type: 'blog', target_id: blog.value.id })
    favorited.value = res?.favorited ?? res?.is_favorited
  } catch (e) { console.error(e); ElMessage.error('操作失败') } finally {
    favoriteLoading.value = false
  }
}

watch(() => route.params.id, (newId) => {
  if (newId) {
    loadBlog(Number(newId)).then(setupTocObserver)
  }
}, { immediate: true })

onUnmounted(() => { tocObserver?.disconnect() })
</script>

<style scoped>
.blog-detail-view {
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
.back-link { margin-bottom: 24px; max-width: 1100px; margin-left: auto; margin-right: auto; }
.state-box { text-align: center; padding: 80px 20px; font-size: 18px; color: #909399; }

.article-layout {
  display: flex;
  gap: 24px;
  max-width: 1100px;
  margin: 0 auto;
  padding: 0 24px;
  align-items: flex-start;
}

.blog-article {
  flex: 1;
  min-width: 0;
  max-width: 800px;
  background: var(--app-bg-card, #fff);
  border: 1px solid var(--app-border, #eee);
  border-radius: 12px;
  padding: 40px;
}
.article-header { margin-bottom: 24px; }
.article-title { font-size: 1.8rem; font-weight: 700; margin: 12px 0 8px; color: var(--app-text); }
.article-author { display: flex; align-items: center; gap: 12px; margin: 12px 0; padding: 12px 0; }
.author-info { display: flex; align-items: center; gap: 8px; }
.author-name { font-weight: 500; color: var(--app-text); }
.author-link { text-decoration: none; color: inherit; }
.author-link:hover .author-name { color: var(--cyber-neon, #00d4aa); }
.article-meta { color: var(--app-text-secondary); font-size: 0.85rem; display: flex; gap: 16px; flex-wrap: wrap; }
.article-tags { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px; }
.article-actions { display: flex; gap: 8px; margin-top: 12px; align-items: center; }
.article-cover { margin: -40px -40px 24px; border-radius: 12px 12px 0 0; overflow: hidden; }
.article-cover img { width: 100%; max-height: 400px; object-fit: cover; display: block; }
.article-content { line-height: 1.8; color: var(--app-text); font-size: 1rem; }

/* 作者卡片 */
.author-card {
  margin-top: 40px;
  padding: 20px;
  background: var(--app-bg);
  border: 1px solid var(--app-border);
  border-radius: 12px;
}
.author-card-main { display: flex; gap: 16px; align-items: flex-start; }
.author-card-avatar { flex-shrink: 0; text-decoration: none; }
.author-card-info { flex: 1; min-width: 0; }
.author-card-name { font-size: 16px; font-weight: 600; color: var(--app-text); text-decoration: none; }
.author-card-name:hover { color: var(--cyber-neon, #00d4aa); }
.author-card-bio { font-size: 13px; color: var(--app-text-secondary); margin: 4px 0 8px; }
.author-card-stats { display: flex; gap: 16px; font-size: 12px; color: var(--app-text-secondary); }
.author-card-actions { flex-shrink: 0; }

/* 相关推荐 */
.related-section { margin-top: 40px; }
.related-title { font-size: 16px; font-weight: 600; margin-bottom: 16px; color: var(--app-text); }
.related-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }
.related-card {
  padding: 16px;
  background: var(--app-bg);
  border: 1px solid var(--app-border);
  border-radius: 8px;
  cursor: pointer;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.related-card:hover {
  border-color: var(--cyber-neon, #00d4aa);
  box-shadow: 0 0 8px rgba(0, 212, 170, 0.1);
}
.related-card-title { font-size: 14px; font-weight: 600; margin: 0 0 6px; color: var(--app-text); display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.related-card-summary { font-size: 12px; color: var(--app-text-secondary); margin: 0 0 8px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.related-card-meta { display: flex; gap: 12px; font-size: 11px; color: var(--app-text-secondary); }

.article-nav { display: flex; justify-content: space-between; margin-top: 40px; padding-top: 20px; border-top: 1px solid var(--app-border); }

/* TOC 侧边栏 */
.toc-sidebar {
  width: 260px;
  flex-shrink: 0;
  position: sticky;
  top: 80px;
  max-height: calc(100vh - 120px);
  overflow-y: auto;
  background: var(--app-bg-card, #fff);
  border: 1px solid var(--app-border);
  border-radius: 12px;
  padding: 16px;
}
.toc-header {
  font-size: 14px;
  font-weight: 600;
  color: var(--app-text);
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--app-border);
}
.toc-nav {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

@media (max-width: 900px) {
  .toc-sidebar { display: none; }
  .article-layout { padding: 0 16px; }
  .blog-article { padding: 20px; }
  .article-cover { margin: -20px -20px 16px; }
  .article-title { font-size: 1.4rem; }
  .related-grid { grid-template-columns: 1fr; }
}
</style>
