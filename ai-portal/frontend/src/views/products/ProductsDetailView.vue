<!-- 产品详情 - 使用 markdown-it 渲染，支持上/下条导航 -->
<template>
  <div class="products-detail-view">
    <div class="reading-progress" :style="{ width: progress + '%' }" />
    <div class="container">
      <!-- 返回按钮 -->
      <div class="back-link">
        <el-button text @click="router.push('/products')">
          <el-icon><ArrowLeft /></el-icon>返回产品列表
        </el-button>
      </div>

      <div v-if="loading" style="text-align:center;padding:80px 0;color:#909399">⏳ 加载中...</div>

      <!-- 产品内容 -->
      <article v-else-if="product" class="product-article">
        <header class="article-header">
          <el-tag :type="getCategoryType(product.category)">{{ product.category }}</el-tag>
          <h1 class="article-title">{{ product.title }}</h1>
          <div class="article-author" v-if="product.author">
            <router-link :to="`/user/${product.author.id}`" class="author-link" :aria-label="product.author.nickname || product.author.username">
              <el-avatar :size="36" :src="product.author.avatar_url">{{ product.author.nickname?.[0] || product.author.username?.[0] }}</el-avatar>
            </router-link>
            <div class="author-info">
              <router-link :to="`/user/${product.author.id}`" class="author-link">
                <span class="author-name">{{ product.author.nickname || product.author.username }}</span>
              </router-link>
              <el-tag size="small" :type="product.author.level === 999 ? 'success' : 'warning'">
                {{ product.author.level === 999 ? '管理员' : 'LV' + product.author.level }}
              </el-tag>
            </div>
          </div>
          <div class="article-meta">
            <span>{{ formatDate(product.created_at) }}</span>
            <span v-if="product.is_published"><el-tag type="success" size="small">已发布</el-tag></span>
            <span v-if="product.view_count">{{ product.view_count }} 次浏览</span>
          </div>
          <div class="article-tags" v-if="product.tags">
            <el-tag v-for="tag in product.tags.split(',')" :key="tag" size="small" effect="plain">{{ tag.trim() }}</el-tag>
          </div>
        </header>

        <div class="article-cover" v-if="product.cover_image">
          <img :src="product.cover_image" :alt="product.title" loading="lazy" @error="(e: Event) => ((e.target as HTMLElement).style.display='none')" />
        </div>

        <div class="article-summary" v-if="product.summary">
          <h3>产品概述</h3>
          <p>{{ product.summary }}</p>
        </div>

        <div class="article-content">
          <h3>产品详情</h3>
          <div class="markdown-body" v-html="renderMd(product.content)"></div>
        </div>

        <div class="article-tags" v-if="product.tags">
          <el-tag v-for="tag in product.tags.split(',')" :key="tag" size="default" effect="light">
            {{ tag.trim() }}
          </el-tag>
        </div>

        <!-- 上下条导航 -->
        <nav class="article-nav">
          <div class="nav-prev">
            <el-button v-if="prevItem" text @click="goTo(prevItem.id)">← {{ prevItem.title }}</el-button>
          </div>
          <div class="nav-next">
            <el-button v-if="nextItem" text @click="goTo(nextItem.id)">{{ nextItem.title }} →</el-button>
          </div>
        </nav>
      </article>

      <!-- 加载失败 -->
      <div v-else style="text-align:center;padding:80px 0">
        <el-empty description="产品不存在" />
        <el-button type="primary" @click="router.push('/products')">返回产品列表</el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ArrowLeft } from '@element-plus/icons-vue'
import { getProductById, listProducts } from '@/api/products'
import { useMarkdown } from '@/composables/useMarkdown'
import { useReadingProgress } from '@/composables/useReadingProgress'

const { renderMd } = useMarkdown()
const { progress } = useReadingProgress()

const router = useRouter()
const route = useRoute()
const loading = ref(true)
const product = ref<any>(null)
const prevItem = ref<any>(null)
const nextItem = ref<any>(null)
const allItems = ref<any[]>([])

const formatDate = (d?: string) => d ? new Date(d).toLocaleString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false }).replace(/\//g, '-') : ''

// 加载所有产品列表（用于上下条导航）
const fetchAllItems = async () => {
  if (allItems.value.length > 0) return allItems.value
  try {
    const res: any = await listProducts()
    allItems.value = Array.isArray(res) ? res : (res?.items || res || [])
  } catch {
    allItems.value = []
  }
  return allItems.value
}

const goTo = (id: number) => {
  router.push(`/products/${id}`)
}

const getCategoryType = (category: string): 'primary' | 'success' | 'warning' | 'info' | 'danger' | undefined => {
  const m: Record<string, 'primary' | 'success' | 'warning' | 'info' | 'danger'> = {
    '大模型应用': 'primary', '机器学习': 'success', '自然语言处理': 'warning',
    '计算机视觉': 'danger', 'AI工程化': 'info', 'SaaS': 'primary', 'PaaS': 'success'
  }
  return m[category]
}

const loadProduct = async (productId: number) => {
  if (!productId) return

  loading.value = true
  prevItem.value = null
  nextItem.value = null

  try {
    const [detail, items] = await Promise.all([
      getProductById(productId),
      fetchAllItems()
    ])
    // @ts-ignore
    product.value = detail

    const idx = items.findIndex((b: any) => Number(b.id) === productId)
    if (idx > 0) prevItem.value = items[idx - 1]
    if (idx < items.length - 1) nextItem.value = items[idx + 1]
  } catch (e) {
    console.error('获取产品详情失败:', e)
    product.value = null
  } finally {
    loading.value = false
  }
}

// 监听路由变化重新加载
watch(() => route.params.id, (newId) => {
  if (newId) {
    loadProduct(Number(newId))
  }
}, { immediate: true })
</script>

<style scoped>
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
.products-detail-view {
  min-height: 100vh;
  background: var(--app-bg);
  padding: 40px 0;
}
.container { max-width: 1000px; margin: 0 auto; padding: 0 20px; }
.back-link { margin-bottom: 30px; }
.back-link .el-button { color: var(--app-accent); font-weight: 500; }

.product-article {
  background: var(--app-bg-card); border-radius: 12px; overflow: hidden;
  box-shadow: var(--el-box-shadow); padding: 40px;
}
.article-header { text-align: center; margin-bottom: 40px; padding-bottom: 20px; border-bottom: 1px solid var(--app-border); }
.article-header .el-tag { margin-bottom: 16px; }
.article-title { font-size: 2.5rem; color: var(--app-text); margin: 12px 0 20px; font-weight: 700; line-height: 1.3; }
.article-author { display: flex; align-items: center; justify-content: center; gap: 12px; margin: 12px 0; }
.author-info { display: flex; align-items: center; gap: 8px; }
.author-name { font-weight: 500; color: var(--app-text); }
.author-link { text-decoration: none; color: inherit; }
.author-link:hover .author-name { color: var(--cyber-neon, #00d4aa); }
.article-meta { color: var(--app-text-secondary); font-size: 0.875rem; display: flex; gap: 16px; justify-content: center; }
.article-tags { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px; justify-content: center; }

.article-cover { margin: 30px 0; border-radius: 8px; overflow: hidden; }
.article-cover img { width: 100%; height: auto; display: block; }

.article-summary { margin-bottom: 40px; padding: 20px; background: var(--app-bg-secondary); border-radius: 8px; }
.article-summary h3 { color: var(--app-text); margin-bottom: 16px; font-weight: 600; }
.article-summary p { color: var(--app-text-secondary); line-height: 1.6; font-size: 1.125rem; }

.article-content { margin-bottom: 40px; }
.article-content h3 { color: var(--app-text); margin-bottom: 16px; font-weight: 600; }

.article-tags { display: flex; flex-wrap: wrap; gap: 12px; margin-bottom: 40px; padding: 20px; background: var(--app-bg-secondary); border-radius: 8px; }

.article-nav {
  display: flex; justify-content: space-between;
  margin-top: 40px; padding-top: 20px;
  border-top: 1px solid var(--app-border);
}
.nav-prev, .nav-next { max-width: 45%; }
.nav-prev .el-button, .nav-next .el-button { text-align: left; white-space: normal; height: auto; line-height: 1.4; }

@media (max-width: 768px) {
  .product-article { padding: 20px; }
  .article-title { font-size: 1.75rem; }
}
</style>
