<template>
  <div class="news-list-view">
    <div class="container">
      <div class="page-header">
        <h1>AI新闻资讯</h1>
        <p class="subtitle">最新的AI技术动态、行业新闻和趋势分析</p>
      </div>

      <div class="filter-section">
        <el-input
          v-model="searchQuery"
          placeholder="搜索新闻..."
          :prefix-icon="Search"
          clearable
          class="search-input"
          @keyup.enter="handleSearch"
          @clear="handleSearch"
        />
        <el-select
          v-model="selectedCategory"
          placeholder="选择分类"
          clearable
          class="category-select"
          @change="handleFilter"
        >
          <el-option label="全部" value="" />
          <el-option
            v-for="cat in categories"
            :key="cat.id || cat"
            :label="cat.name || cat"
            :value="cat.name || cat"
          />
        </el-select>
        <el-select v-model="sortBy" class="sort-select" @change="handleFilter">
          <el-option label="最新发布" value="latest" />
          <el-option label="最多浏览" value="views" />
          <el-option label="最多点赞" value="likes" />
        </el-select>
      </div>

      <div class="news-layout">
        <div class="news-main">
          <ContentCardSkeleton v-if="loading" :count="4" />
          <div v-else class="news-list">
            <div
              v-for="news in newsList"
              :key="news.id"
              class="news-card"
              @click="goToDetail(news.id)"
            >
              <div class="news-cover" v-if="news.cover_image">
                <img :src="news.cover_image" :alt="news.title" />
              </div>
              <div class="news-content">
                <div class="news-meta">
                  <el-tag :type="getCategoryType(news.category)" size="small">{{ news.category }}</el-tag>
                  <span class="author-info" v-if="news.author" @click.stop>
                    <router-link :to="`/user/${news.author.id}`" class="author-link">{{ news.author.nickname || news.author.username }}</router-link>
                  </span>
                  <span class="publish-date">{{ formatDate(news.created_at) }}</span>
                </div>
                <h3 class="news-title">{{ news.title }}</h3>
                <p class="news-summary">{{ news.summary || '' }}</p>
                <div class="news-footer">
                  <div class="tags" v-if="news.tags">
                    <el-tag
                      v-for="(tag, index) in parseTags(news.tags)"
                      :key="tag + '-' + index"
                      size="small"
                      effect="light"
                    >{{ tag }}</el-tag>
                  </div>
                  <div class="news-stats">
                    <span v-if="news.view_count"><el-icon><View /></el-icon> {{ news.view_count }}</span>
                    <span v-if="news.likes_count"><el-icon><Star /></el-icon> {{ news.likes_count }}</span>
                    <span v-if="news.comments_count"><el-icon><ChatDotRound /></el-icon> {{ news.comments_count }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div v-if="!loading && newsList.length === 0" class="empty-state">
            <el-empty description="暂无新闻资讯" />
          </div>

          <div class="pagination" v-if="total > pageSize">
            <el-pagination
              v-model:current-page="currentPage"
              v-model:page-size="pageSize"
              :page-sizes="[6, 12, 24]"
              :total="total"
              layout="total, sizes, prev, pager, next"
              @size-change="handleSizeChange"
              @current-change="handleCurrentChange"
            />
          </div>
        </div>

        <aside class="news-sidebar">
          <el-card class="sidebar-card">
            <template #header><span>热门标签</span></template>
            <div class="tag-cloud">
              <el-tag
                v-for="tag in hotTags"
                :key="tag.id || tag"
                size="small"
                :type="tagTypes[Math.floor(Math.random() * tagTypes.length)]"
                class="hot-tag"
                @click="filterByTag(tag.name || tag)"
              >{{ tag.name || tag }}</el-tag>
            </div>
          </el-card>
        </aside>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Search, View, Star, ChatDotRound } from '@element-plus/icons-vue'
import { listNews } from '@/api/news'
import { fetchCategories } from '@/api/category'
import { fetchPopularTags } from '@/api/tag'
import { ContentCardSkeleton } from '@/components/skeleton'

const router = useRouter()
const route = useRoute()
const loading = ref(false)
const newsList = ref<any[]>([])
const searchQuery = ref('')
const selectedCategory = ref('')
const sortBy = ref('latest')
const currentPage = ref(1)
const pageSize = ref(12)
const total = ref(0)
const categories = ref<any[]>([])
const hotTags = ref<any[]>([])
const tagTypes: Array<'primary' | 'success' | 'warning' | 'danger' | 'info'> = ['primary', 'success', 'warning', 'danger', 'info']

const fetchNews = async () => {
  loading.value = true
  try {
    const params: any = {
      page: currentPage.value,
      page_size: pageSize.value,
    }
    if (selectedCategory.value) params.category = selectedCategory.value
    if (searchQuery.value) params.keyword = searchQuery.value
    const res: any = await listNews(params)
    const data = res?.items || res?.data || (Array.isArray(res) ? res : [])
    newsList.value = data
    total.value = res?.total || data.length
  } catch (error) {
    console.error('获取新闻列表失败:', error)
  } finally {
    loading.value = false
  }
}

const fetchCategoriesList = async () => {
  try {
    const res: any = await fetchCategories({ module_type: 'news', page_size: 50 })
    categories.value = res.items || res || []
  } catch {}
}

const fetchHotTags = async () => {
  try {
    const res: any = await fetchPopularTags(20)
    hotTags.value = res || []
  } catch {}
}

const handleSearch = () => {
  currentPage.value = 1
  fetchNews()
}

const handleFilter = () => {
  currentPage.value = 1
  fetchNews()
}

const handleSizeChange = () => {
  currentPage.value = 1
  fetchNews()
}

const handleCurrentChange = () => {
  fetchNews()
}

const goToDetail = (id: number) => {
  router.push(`/news/${id}`)
}

const filterByTag = (tagName: string) => {
  searchQuery.value = tagName
  handleSearch()
}

const getCategoryType = (category: string): 'primary' | 'success' | 'warning' | 'info' | 'danger' | undefined => {
  const map: Record<string, 'primary' | 'success' | 'warning' | 'info' | 'danger'> = {
    '行业动态': 'primary', '技术前沿': 'success', '企业新闻': 'warning',
    '政策法规': 'danger', '投资融资': 'info', '产品发布': 'info',
  }
  return map[category] || 'info'
}

const parseTags = (tags: string) => {
  if (!tags) return []
  return tags.split(',').filter(Boolean).map((t: string) => t.trim())
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' })
}

onMounted(() => {
  if (route.query.tag) {
    searchQuery.value = route.query.tag as string
  }
  fetchNews()
  fetchCategoriesList()
  fetchHotTags()
})
</script>

<style scoped>
.author-link { text-decoration: none; color: var(--app-text-secondary); }
.author-link:hover { color: var(--cyber-neon, #00d4aa); }
.news-list-view {
  min-height: 100vh;
  background: var(--app-bg, #f5f7fa);
  padding: 40px 0;
}
.container { max-width: 1200px; margin: 0 auto; padding: 0 20px; }
.page-header { text-align: center; margin-bottom: 40px; }
.page-header h1 { font-size: 2.4rem; color: var(--app-text); margin-bottom: 10px; font-weight: 700; }
.subtitle { font-size: 1.1rem; color: var(--app-text-secondary); font-weight: 300; }

.filter-section { display: flex; gap: 12px; margin-bottom: 24px; flex-wrap: wrap; }
.search-input { flex: 1; min-width: 200px; }
.category-select { min-width: 160px; }
.sort-select { min-width: 120px; }

.news-layout { display: grid; grid-template-columns: 3fr 1fr; gap: 24px; }
.news-main { min-width: 0; }

.news-list { display: flex; flex-direction: column; gap: 16px; }
.news-card {
  background: var(--app-bg-card, white);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  transition: box-shadow 0.3s, transform 0.3s;
  cursor: pointer;
  display: flex;
}
.news-card:hover { transform: translateY(-2px); box-shadow: 0 8px 24px rgba(0,0,0,0.12); }

.news-cover { width: 200px; flex-shrink: 0; overflow: hidden; }
.news-cover img { width: 100%; height: 100%; object-fit: cover; transition: transform 0.3s; display: block; }
.news-card:hover .news-cover img { transform: scale(1.05); }

.news-content { padding: 20px; flex: 1; min-width: 0; }
.news-meta { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; font-size: 13px; color: var(--app-text-secondary); }
.news-title { font-size: 1.2rem; color: var(--app-text); margin-bottom: 8px; font-weight: 600; line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.news-summary { color: var(--app-text-secondary); line-height: 1.6; margin-bottom: 12px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; font-size: 14px; }
.news-footer { display: flex; justify-content: space-between; align-items: center; }
.tags { display: flex; gap: 6px; flex-wrap: wrap; }
.news-stats { display: flex; gap: 12px; font-size: 13px; color: var(--app-text-secondary); }
.news-stats .el-icon { margin-right: 2px; }

.news-sidebar { position: sticky; top: 80px; }
.sidebar-card { margin-bottom: 16px; }
.tag-cloud { display: flex; flex-wrap: wrap; gap: 6px; }
.hot-tag { cursor: pointer; transition: transform 0.2s; }
.hot-tag:hover { transform: scale(1.05); }

.pagination { display: flex; justify-content: center; margin-top: 32px; }
.empty-state { text-align: center; padding: 60px 0; }

@media (max-width: 900px) {
  .news-layout { grid-template-columns: 1fr; }
  .news-sidebar { position: static; }
}
@media (max-width: 768px) {
  .page-header h1 { font-size: 1.8rem; }
  .filter-section { flex-direction: column; }
  .news-card { flex-direction: column; }
  .news-cover { width: 100%; height: 180px; }
}
</style>
