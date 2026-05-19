<template>
  <div class="project-detail-view">
    <div class="container">
      <div class="back-link">
        <el-button text @click="router.push('/portfolio')">
          <el-icon><ArrowLeft /></el-icon>返回作品集
        </el-button>
      </div>

      <div v-if="loading" class="state-box">
        <el-skeleton :rows="10" animated />
      </div>

      <article v-else-if="project" class="project-article">
        <header class="article-header">
          <el-tag size="small" type="primary">{{ project.category }}</el-tag>
          <h1 class="article-title">{{ project.title }}</h1>
          <div class="article-author" v-if="project.author">
            <router-link :to="`/user/${project.author.id}`" class="author-link" :aria-label="project.author.nickname || project.author.username">
              <el-avatar :size="36" :src="project.author.avatar_url">{{ project.author.nickname?.[0] || project.author.username?.[0] }}</el-avatar>
            </router-link>
            <div class="author-info">
              <router-link :to="`/user/${project.author.id}`" class="author-link">
                <span class="author-name">{{ project.author.nickname || project.author.username }}</span>
              </router-link>
              <el-tag size="small" :type="project.author.level === 999 ? 'success' : 'warning'">
                {{ project.author.level === 999 ? '管理员' : 'LV' + project.author.level }}
              </el-tag>
            </div>
          </div>
          <div class="article-meta">
            <span>发布时间: {{ formatDate(project.created_at) }}</span>
          </div>
          <div class="article-actions">
            <el-button size="small" @click="toggleLike" :type="liked ? 'danger' : 'default'">
              {{ liked ? '❤️' : '🤍' }} {{ likesCount }}
            </el-button>
            <el-button size="small" @click="toggleFavorite" :type="favorited ? 'warning' : 'default'">
              {{ favorited ? '⭐' : '☆' }} 收藏
            </el-button>
            <el-button size="small" v-if="isAuthor" type="primary" @click="editProject">编辑</el-button>
          </div>
        </header>

        <div class="article-cover" v-if="project.cover_image">
          <img :src="project.cover_image" :alt="project.title" />
        </div>

        <div class="article-summary" v-if="project.description">
          <p>{{ project.description }}</p>
        </div>

        <div class="article-content markdown-body" v-if="project.content" v-html="renderMd(project.content)"></div>
        <div class="article-content" v-else>
          <p style="color: #666;">（暂无详细内容）</p>
        </div>

        <div class="article-tags" v-if="project.tech_stack && project.tech_stack.length">
          <h3>技术栈</h3>
          <div class="tags-container">
            <el-tag v-for="tech in project.tech_stack" :key="tech" size="default" effect="plain">
              {{ tech }}
            </el-tag>
          </div>
        </div>

        <div class="article-links" v-if="project.demo_url || project.repo_url">
          <el-button type="primary" v-if="project.demo_url" @click="openLink(project.demo_url)">查看 Demo</el-button>
          <el-button v-if="project.repo_url" @click="openLink(project.repo_url)">开源仓库</el-button>
        </div>
      </article>

      <div v-else class="state-box error">
        <el-empty description="项目不存在或加载失败" />
        <el-button type="primary" @click="router.push('/portfolio')">返回作品集</el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ArrowLeft } from '@element-plus/icons-vue'
import { getProject } from '@/api/portfolio'
import { toggleLike as apiToggleLike, toggleFavorite as apiToggleFavorite, checkLiked, checkFavorited } from '@/api/interaction'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import MarkdownIt from 'markdown-it'

const md = new MarkdownIt({ html: false, linkify: true, typographer: true })
const renderMd = (src?: string) => src ? md.render(src) : ''

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const loading = ref(true)
const project = ref<any>(null)
const liked = ref(false)
const favorited = ref(false)
const likesCount = ref(0)
const likeLoading = ref(false)
const favoriteLoading = ref(false)

const isAuthor = computed(() => {
  return authStore.user && project.value && authStore.user.id === (project.value.author?.id || project.value.author_id)
})

const formatDate = (d?: string) => d ? new Date(d).toLocaleString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false }).replace(/\//g, '-') : ''
const openLink = (url: string) => window.open(url, '_blank')

const loadProject = async (id: number) => {
  if (!id) return
  loading.value = true
  try {
    const res: any = await getProject(id)
    project.value = res.data || res
    likesCount.value = project.value?.likes_count || 0
    if (authStore.isLoggedIn) {
      try {
        const [ls, fs]: any[] = await Promise.all([
          checkLiked('project', id),
          checkFavorited('project', id),
        ])
        liked.value = ls?.liked || ls?.is_liked
        favorited.value = fs?.favorited || fs?.is_favorited
      } catch (e) { console.error(e) }
    }
  } catch (e) {
    console.error('Failed to load project:', e)
    project.value = null
  } finally {
    loading.value = false
  }
}

const toggleLike = async () => {
  if (!authStore.isLoggedIn || !project.value || likeLoading.value) return
  likeLoading.value = true
  try {
    const res: any = await apiToggleLike({ target_type: 'project', target_id: project.value.id })
    liked.value = res?.liked ?? res?.is_liked ?? !liked.value
    likesCount.value = res?.likes_count ?? res?.count ?? likesCount.value
  } catch (e) { console.error(e); ElMessage.error('操作失败') } finally {
    likeLoading.value = false
  }
}

const toggleFavorite = async () => {
  if (!authStore.isLoggedIn || !project.value || favoriteLoading.value) return
  favoriteLoading.value = true
  try {
    const res: any = await apiToggleFavorite({ target_type: 'project', target_id: project.value.id })
    favorited.value = res?.favorited ?? res?.is_favorited ?? !favorited.value
  } catch (e) { console.error(e); ElMessage.error('操作失败') } finally {
    favoriteLoading.value = false
  }
}

const editProject = () => router.push('/admin/projects')

watch(() => route.params.id, (newId) => {
  if (newId) {
    loadProject(Number(newId))
  }
}, { immediate: true })
</script>

<style scoped>
.project-detail-view {
  min-height: calc(100vh - 100px);
  background: var(--el-bg-color-page);
  padding: 40px 0;
}
.container {
  max-width: 900px;
  margin: 0 auto;
  padding: 0 20px;
}
.back-link {
  margin-bottom: 24px;
}
.state-box {
  padding: 60px 0;
  text-align: center;
}
.project-article {
  background: var(--el-bg-color);
  border-radius: 12px;
  padding: 40px;
  box-shadow: var(--el-box-shadow-light);
}
.article-header {
  margin-bottom: 24px;
}
.article-title {
  font-size: 2rem;
  margin: 16px 0;
  color: var(--el-text-color-primary);
}
.article-author {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 12px 0;
}
.author-info {
  display: flex;
  align-items: center;
  gap: 8px;
}
.author-name {
  font-weight: 500;
  color: var(--app-text);
}
.author-link { text-decoration: none; color: inherit; }
.author-link:hover .author-name { color: var(--cyber-neon, #00d4aa); }
.article-meta {
  color: var(--el-text-color-secondary);
  font-size: 0.9rem;
}
.article-actions { display: flex; gap: 8px; margin-top: 12px; }
.article-cover {
  margin: 24px -40px;
  max-height: 400px;
  overflow: hidden;
  background: var(--el-fill-color-light);
}
.article-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.article-summary {
  font-size: 1.1rem;
  line-height: 1.6;
  color: var(--el-text-color-regular);
  padding: 20px;
  background: var(--el-fill-color-light);
  border-radius: 8px;
  margin-bottom: 32px;
}
.article-content {
  line-height: 1.8;
  margin-bottom: 32px;
}
.article-tags {
  margin-bottom: 32px;
}
.article-tags h3 {
  margin-bottom: 16px;
  font-size: 1.2rem;
}
.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}
.article-links {
  display: flex;
  gap: 16px;
  padding-top: 24px;
  border-top: 1px solid var(--el-border-color-lighter);
}
</style>