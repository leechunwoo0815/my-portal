<template>
  <div class="series-detail-view">
    <div class="container">
      <div class="back-link">
        <el-button text @click="$router.push('/series')">
          <el-icon><ArrowLeft /></el-icon>返回专栏列表
        </el-button>
      </div>

      <div v-if="loading" class="loading-state">加载中...</div>

      <template v-else-if="series">
        <div class="series-header">
          <div class="series-cover" v-if="series.cover_image">
            <img :src="series.cover_image" :alt="series.title" />
          </div>
          <div class="series-meta">
            <h1>{{ series.title }}</h1>
            <p class="series-desc">{{ series.description || '' }}</p>
            <div class="series-stats">
              <span>{{ series.articles_count || 0 }} 篇文章</span>
              <span>创建于 {{ formatDate(series.created_at) }}</span>
            </div>
          </div>
        </div>

        <div class="articles-list">
          <div v-for="(article, idx) in articles" :key="article.id" class="article-item" @click="$router.push(`/blog/${article.id}`)">
            <span class="article-order">{{ idx + 1 }}</span>
            <div class="article-info">
              <h3>{{ article.title }}</h3>
              <p v-if="article.summary">{{ article.summary }}</p>
              <div class="article-meta">
                <span>{{ article.view_count || 0 }} 阅读</span>
                <span>{{ article.likes_count || 0 }} 点赞</span>
              </div>
            </div>
          </div>
          <el-empty v-if="articles.length === 0" description="专栏暂无文章" />
        </div>
      </template>

      <div v-else class="state-box">专栏不存在</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ArrowLeft } from '@element-plus/icons-vue'
import { seriesApi } from '@/api/series'

const route = useRoute()
const loading = ref(true)
const series = ref<any>(null)
const articles = ref<any[]>([])

const formatDate = (d: string) => d ? new Date(d).toLocaleDateString('zh-CN') : ''

const loadSeries = async () => {
  loading.value = true
  try {
    const res: any = await seriesApi.get(Number(route.params.id))
    series.value = res
    articles.value = res.articles || []
  } catch { series.value = null }
  finally { loading.value = false }
}

onMounted(loadSeries)
</script>

<style scoped>
.series-detail-view { min-height: 100vh; background: var(--app-bg); padding: 32px 0; }
.container { max-width: 800px; margin: 0 auto; padding: 0 20px; }
.back-link { margin-bottom: 24px; }
.loading-state { text-align: center; padding: 80px; color: var(--app-text-secondary); }
.state-box { text-align: center; padding: 80px; color: var(--app-text-secondary); }

.series-header { margin-bottom: 32px; }
.series-cover { height: 200px; border-radius: 12px; overflow: hidden; margin-bottom: 16px; }
.series-cover img { width: 100%; height: 100%; object-fit: cover; }
.series-meta h1 { font-size: 1.8rem; margin: 0 0 8px; }
.series-desc { color: var(--app-text-secondary); margin: 0 0 12px; }
.series-stats { display: flex; gap: 16px; font-size: 13px; color: var(--app-text-secondary); }

.articles-list { display: flex; flex-direction: column; gap: 12px; }
.article-item {
  display: flex;
  gap: 16px;
  padding: 16px;
  background: var(--app-bg-card);
  border: 1px solid var(--app-border);
  border-radius: 8px;
  cursor: pointer;
  transition: border-color 0.2s;
}
.article-item:hover { border-color: var(--cyber-neon); }
.article-order {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--cyber-neon);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 14px;
  flex-shrink: 0;
}
.article-info { flex: 1; }
.article-info h3 { font-size: 15px; margin: 0 0 4px; }
.article-info p { font-size: 13px; color: var(--app-text-secondary); margin: 0 0 4px; }
.article-meta { display: flex; gap: 12px; font-size: 12px; color: var(--app-text-secondary); }
</style>
