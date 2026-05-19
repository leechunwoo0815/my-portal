<template>
  <div class="user-content-view">
    <div class="content-tabs">
      <el-tabs v-model="activeTab">
        <el-tab-pane label="文章" name="blogs">
          <div v-if="blogs.length === 0" class="empty"><el-empty description="暂无文章" /></div>
          <div v-else class="content-list">
            <div v-for="item in blogs" :key="item.id" class="content-item" role="button" tabindex="0" @click="goToBlog(item.id)" @keydown.enter="goToBlog(item.id)">
              <h4>{{ item.title }}</h4>
              <p class="summary">{{ item.summary }}</p>
              <div class="meta">
                <span>{{ formatDate(item.created_at) }}</span>
                <span><el-icon><View /></el-icon> {{ item.view_count || 0 }}</span>
                <span><el-icon><Star /></el-icon> {{ item.likes_count || 0 }}</span>
              </div>
            </div>
          </div>
        </el-tab-pane>
        <el-tab-pane label="收藏" name="favorites">
          <div v-if="favorites.length === 0" class="empty"><el-empty description="暂无收藏" /></div>
          <div v-else class="content-list">
            <div v-for="item in favorites" :key="item.id" class="content-item" role="button" tabindex="0" @click="goToDetail(item)" @keydown.enter="goToDetail(item)">
              <h4>{{ item.title }}</h4>
              <p class="summary">{{ item.summary }}</p>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { View, Star } from '@element-plus/icons-vue'
import { listBlogs } from '@/api/blog'
import { fetchUserFavorites } from '@/api/interaction'

const route = useRoute()
const router = useRouter()
const activeTab = ref('blogs')
const blogs = ref<any[]>([])
const favorites = ref<any[]>([])
const userId = ref<number>(0)

const fetchBlogs = async () => {
  if (!userId.value) return
  try {
    const res: any = await listBlogs({ author_id: userId.value, page_size: 50 })
    blogs.value = res.items || res || []
  } catch { blogs.value = [] }
}

const fetchFavorites = async () => {
  try {
    const res: any = await fetchUserFavorites({ page_size: 50 })
    favorites.value = res.items || res || []
  } catch { favorites.value = [] }
}

const goToBlog = (id: number) => router.push(`/blog/${id}`)
const goToDetail = (item: any) => {
  const map: Record<string, string> = { blog: '/blog', news: '/news', product: '/products', solution: '/solutions' }
  const path = map[item.target_type] || '/blog'
  router.push(`${path}/${item.target_id}`)
}

const formatDate = (v: string) => {
  if (!v) return ''
  const d = new Date(v)
  return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`
}

watch(() => route.params.id, (id) => {
  if (id) {
    userId.value = Number(id)
    fetchBlogs()
    fetchFavorites()
  }
}, { immediate: true })
</script>

<style scoped>
.user-content-view { max-width: 800px; margin: 0 auto; padding: 20px; }
.content-list { display: flex; flex-direction: column; gap: 12px; }
.content-item { padding: 16px; border-radius: 8px; background: var(--app-bg-card, white); cursor: pointer; transition: background 0.2s; }
.content-item:hover { background: var(--el-fill-color-light); }
.content-item h4 { margin: 0 0 8px; font-size: 15px; }
.summary { font-size: 13px; color: var(--el-text-color-secondary); margin: 0 0 8px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.meta { display: flex; gap: 16px; font-size: 12px; color: var(--el-text-color-placeholder); }
.empty { padding: 40px 0; }
</style>
