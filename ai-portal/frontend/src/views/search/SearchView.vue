<template>
  <div class="search-view">
    <div class="search-header">
      <h2 class="font-mono">[ 搜索 ]</h2>
      <div class="search-input-wrapper">
        <el-input
          v-model="keyword"
          placeholder="输入关键词搜索..."
          size="large"
          clearable
          @keyup.enter="doSearch"
          @input="onInput"
          @focus="showSuggestions = true"
          @blur="onBlur"
        >
          <template #prefix>
            <span class="input-prefix font-mono">>_</span>
          </template>
          <template #append>
            <el-button :icon="Search" aria-label="搜索" @click="doSearch" />
          </template>
        </el-input>

        <transition name="suggestion-fade">
          <div v-if="hasSuggestions" class="suggestions-dropdown">
            <div class="suggestion-section" v-if="autocompleteResults.length">
              <div class="suggestion-header">
                <span class="font-mono">搜索建议</span>
              </div>
              <div
                v-for="(s, idx) in autocompleteResults"
                :key="'ac-' + idx"
                class="suggestion-item"
                @mousedown.prevent="applySuggestion(s)"
              >
                <el-icon><Search /></el-icon>
                <span>{{ s }}</span>
              </div>
            </div>
            <div class="suggestion-section" v-if="searchHistory.length">
              <div class="suggestion-header">
                <span class="font-mono">搜索历史</span>
                <el-button text size="small" @click="clearHistory">清空</el-button>
              </div>
              <div
                v-for="(h, idx) in searchHistory.slice(0, 8)"
                :key="idx"
                class="suggestion-item"
                @mousedown.prevent="applySuggestion(h)"
              >
                <el-icon><Clock /></el-icon>
                <span>{{ h }}</span>
              </div>
            </div>
            <div class="suggestion-section" v-if="trendingTags.length">
              <div class="suggestion-header">
                <span class="font-mono">热门搜索</span>
              </div>
              <div class="trending-tags">
                <el-tag
                  v-for="tag in trendingTags.slice(0, 10)"
                  :key="tag.name"
                  size="small"
                  effect="plain"
                  class="trending-tag"
                  @mousedown.prevent="applySuggestion(tag.name)"
                >
                  {{ tag.name }}
                </el-tag>
              </div>
            </div>
          </div>
        </transition>
      </div>

      <div class="search-filters">
        <el-radio-group v-model="targetType" @change="doSearch">
          <el-radio-button label="">全部</el-radio-button>
          <el-radio-button label="blog">博客</el-radio-button>
          <el-radio-button label="news">资讯</el-radio-button>
          <el-radio-button label="product">产品</el-radio-button>
          <el-radio-button label="solution">方案</el-radio-button>
        </el-radio-group>
      </div>
    </div>

    <div class="search-results">
      <SearchResultSkeleton v-if="loading" :count="5" />
      <div v-if="results.length === 0 && !loading && hasSearched" class="no-results">
        <div class="no-results-icon">🔍</div>
        <p>未找到相关内容</p>
        <p class="no-results-hint">试试其他关键词或浏览推荐内容</p>
      </div>
      <div v-else-if="results.length > 0">
        <p class="result-count font-mono">共找到 <span class="text-cyber-neon">{{ total }}</span> 条结果</p>
        <div class="result-list">
          <div
            v-for="item in results"
            :key="`${item.target_type}-${item.id}`"
            class="result-item"
            @click="goToDetail(item)"
          >
            <div v-if="item.cover_image" class="result-item__cover">
              <img :src="item.cover_image" :alt="item.title" @error="($event.target as HTMLImageElement).style.display='none'" />
            </div>
            <div class="result-item__type">
              <el-tag size="small" :type="typeTagMap[item.target_type] || 'info'">
                {{ typeNameMap[item.target_type] || item.target_type }}
              </el-tag>
            </div>
            <div class="result-item__content">
              <h3 class="result-item__title">{{ item.title }}</h3>
              <p class="result-item__summary" v-if="item.summary">{{ item.summary }}</p>
              <div class="result-item__tags" v-if="item.tags">
                <el-tag v-for="tag in item.tags.split(',').slice(0, 3)" :key="tag" size="small" effect="plain" type="info">{{ tag.trim() }}</el-tag>
              </div>
              <div class="result-item__meta">
                <span v-if="item.author_name">{{ item.author_name }}</span>
                <span v-if="item.view_count">👁 {{ item.view_count }}</span>
                <span v-if="item.likes_count">♡ {{ item.likes_count }}</span>
                <span v-if="item.created_at">{{ formatDate(item.created_at) }}</span>
              </div>
            </div>
          </div>
        </div>
        <el-pagination
          v-if="total > pageSize"
          v-model:current-page="page"
          :page-size="pageSize"
          :total="total"
          layout="prev, pager, next"
          @current-change="doSearch"
          class="pagination"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Search, Clock } from '@element-plus/icons-vue'
import { searchContent, searchSuggest } from '@/api/search'
import { recommendApi } from '@/api/recommend'
import { SearchResultSkeleton } from '@/components/skeleton'

const route = useRoute()
const router = useRouter()

const keyword = ref('')
const targetType = ref('')
const results = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const loading = ref(false)
const hasSearched = ref(false)
const showSuggestions = ref(false)
const searchHistory = ref<string[]>([])
const trendingTags = ref<any[]>([])
const autocompleteResults = ref<string[]>([])
let autocompleteTimer: ReturnType<typeof setTimeout> | null = null

const HISTORY_KEY = 'search_history'
const MAX_HISTORY = 20

const typeTagMap: Record<string, '' | 'primary' | 'success' | 'warning' | 'danger' | 'info'> = {
  blog: 'primary',
  news: 'warning',
  product: 'success',
  solution: 'info',
}

const typeNameMap: Record<string, string> = {
  blog: '博客',
  news: '资讯',
  product: '产品',
  solution: '方案',
}

const loadHistory = () => {
  try {
    const raw = localStorage.getItem(HISTORY_KEY)
    searchHistory.value = raw ? JSON.parse(raw) : []
  } catch {
    searchHistory.value = []
  }
}

const saveHistory = (kw: string) => {
  const trimmed = kw.trim()
  if (!trimmed) return
  const list = searchHistory.value.filter(h => h !== trimmed)
  list.unshift(trimmed)
  searchHistory.value = list.slice(0, MAX_HISTORY)
  localStorage.setItem(HISTORY_KEY, JSON.stringify(searchHistory.value))
}

const clearHistory = () => {
  searchHistory.value = []
  localStorage.removeItem(HISTORY_KEY)
}

const applySuggestion = (text: string) => {
  keyword.value = text
  showSuggestions.value = false
  doSearch()
}

const onBlur = () => {
  setTimeout(() => {
    showSuggestions.value = false
  }, 200)
}

const onInput = () => {
  const q = keyword.value.trim()
  showSuggestions.value = q.length > 0
  if (autocompleteTimer) clearTimeout(autocompleteTimer)
  if (q.length < 2) { autocompleteResults.value = []; return }
  autocompleteTimer = setTimeout(async () => {
    try {
      const res: any = await searchSuggest(q)
      autocompleteResults.value = Array.isArray(res) ? res : (res.data || [])
    } catch { autocompleteResults.value = [] }
  }, 300)
}

const hasSuggestions = computed(() => showSuggestions.value && (autocompleteResults.value.length || searchHistory.value.length || trendingTags.value.length))

const doSearch = async () => {
  if (!keyword.value.trim()) return
  showSuggestions.value = false
  saveHistory(keyword.value.trim())
  loading.value = true
  hasSearched.value = true
  try {
    const res: any = await searchContent({
      keyword: keyword.value.trim(),
      target_type: targetType.value || undefined,
      page: page.value,
      page_size: pageSize.value,
    })
    results.value = res.items || []
    total.value = res.total || 0
  } catch {
    results.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

const goToDetail = (item: any) => {
  const pathMap: Record<string, string> = {
    blog: '/blog',
    news: '/news',
    product: '/products',
    solution: '/solutions',
  }
  const basePath = pathMap[item.target_type] || '/blog'
  router.push(`${basePath}/${item.id}`)
}

const formatDate = (v: string) => {
  if (!v) return ''
  const d = new Date(v)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

const loadTrendingTags = async () => {
  try {
    const res: any = await recommendApi.getTrendingTags(10)
    trendingTags.value = res.tags || []
  } catch {}
}

onMounted(() => {
  loadHistory()
  loadTrendingTags()
  if (route.query.q) {
    keyword.value = route.query.q as string
    doSearch()
  }
})
</script>

<style scoped>
.search-view {
  max-width: 800px;
  margin: 0 auto;
  padding: 24px 16px;
}
.search-header {
  margin-bottom: 24px;
}
.search-header h2 {
  margin: 0 0 16px;
  color: var(--cyber-text, var(--app-text));
}
.search-input-wrapper {
  position: relative;
  margin-bottom: 16px;
}
.input-prefix {
  color: var(--cyber-neon, var(--app-accent));
  font-size: 0.85rem;
  margin-right: 4px;
}
.search-filters {
  margin-bottom: 8px;
}

.suggestions-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: var(--cyber-card, var(--app-bg-card));
  border: 1px solid var(--cyber-border, var(--app-border));
  border-radius: 8px;
  margin-top: 4px;
  z-index: 100;
  box-shadow: 0 4px 16px rgba(0,0,0,0.15);
  overflow: hidden;
}
.suggestion-section {
  padding: 8px 0;
  border-bottom: 1px solid var(--cyber-border, var(--app-border));
}
.suggestion-section:last-child {
  border-bottom: none;
}
.suggestion-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 16px;
  font-size: 0.78rem;
  color: var(--cyber-muted, var(--app-text-secondary));
}
.suggestion-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  cursor: pointer;
  font-size: 0.85rem;
  color: var(--cyber-text, var(--app-text));
  transition: background 0.15s;
}
.suggestion-item:hover {
  background: var(--cyber-bg, var(--app-bg-secondary));
}
.suggestion-item .el-icon {
  color: var(--cyber-muted, var(--app-text-secondary));
  font-size: 14px;
}
.trending-tags {
  padding: 8px 16px;
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.trending-tag {
  cursor: pointer;
  transition: transform 0.15s;
}
.trending-tag:hover {
  transform: translateY(-1px);
}

.suggestion-fade-enter-active { transition: opacity 0.15s, transform 0.15s; }
.suggestion-fade-leave-active { transition: opacity 0.1s; }
.suggestion-fade-enter-from { opacity: 0; transform: translateY(-4px); }
.suggestion-fade-leave-to { opacity: 0; }

.result-count {
  color: var(--cyber-muted, var(--app-text-secondary));
  font-size: 14px;
  margin: 0 0 16px;
}
.result-item {
  display: flex;
  gap: 12px;
  padding: 16px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s, border-color 0.2s;
  border: 1px solid transparent;
  border-bottom-color: var(--cyber-border, var(--app-border));
  margin-bottom: 4px;
  align-items: flex-start;
}
.result-item:hover {
  background: var(--cyber-card, var(--app-bg-card));
  border-color: var(--cyber-neon, var(--app-accent));
}
.result-item__cover {
  flex-shrink: 0;
  width: 80px;
  height: 60px;
  border-radius: 6px;
  overflow: hidden;
}
.result-item__cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.result-item__content {
  flex: 1;
  min-width: 0;
}
.result-item__title {
  margin: 0 0 4px;
  font-size: 16px;
  font-weight: 500;
  color: var(--cyber-text, var(--app-text));
}
.result-item__summary {
  margin: 0 0 8px;
  font-size: 13px;
  color: var(--cyber-muted, var(--app-text-secondary));
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.result-item__meta {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: var(--cyber-muted, var(--app-text-secondary));
}
.result-item__tags {
  display: flex;
  gap: 4px;
  margin-bottom: 6px;
  flex-wrap: wrap;
}
.pagination {
  margin-top: 24px;
  justify-content: center;
}

.no-results {
  text-align: center;
  padding: 60px 20px;
}
.no-results-icon {
  font-size: 48px;
  margin-bottom: 16px;
}
.no-results p {
  color: var(--cyber-muted, var(--app-text-secondary));
  margin-bottom: 8px;
}
.no-results-hint {
  font-size: 0.85rem;
  opacity: 0.7;
}
</style>
