<template>
  <div class="history-view">
    <div class="container">
      <div class="page-header">
        <h1>阅读历史</h1>
        <el-button v-if="historyList.length" text type="danger" @click="handleClear">清空历史</el-button>
      </div>

      <div v-if="loading" class="loading-state">加载中...</div>

      <el-empty v-else-if="historyList.length === 0" description="暂无阅读记录">
        <el-button type="primary" @click="$router.push('/blog')">去阅读</el-button>
      </el-empty>

      <div v-else class="history-list">
        <div
          v-for="item in historyList"
          :key="item.id"
          class="history-item"
          @click="goToDetail(item)"
        >
          <el-tag size="small" :type="typeMap[item.content_type]?.type || 'info'">
            {{ typeMap[item.content_type]?.label || item.content_type }}
          </el-tag>
          <div class="history-info">
            <h4>{{ item.content_title || '未知内容' }}</h4>
            <span class="history-time">{{ formatTime(item.read_at) }}</span>
          </div>
        </div>
      </div>

      <el-pagination
        v-if="total > pageSize"
        v-model:current-page="page"
        :page-size="pageSize"
        :total="total"
        layout="prev, pager, next"
        @current-change="fetchHistory"
        class="pagination"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { historyApi } from '@/api/history'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const loading = ref(false)
const historyList = ref<any[]>([])
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)

const typeMap: Record<string, { label: string; type: '' | 'primary' | 'success' | 'warning' | 'danger' | 'info' }> = {
  blog: { label: '博客', type: 'primary' },
  news: { label: '资讯', type: 'warning' },
  product: { label: '产品', type: 'success' },
  solution: { label: '方案', type: 'info' },
}

const fetchHistory = async () => {
  loading.value = true
  try {
    const res: any = await historyApi.list(page.value, pageSize.value)
    historyList.value = res.items || []
    total.value = res.total || 0
  } catch { historyList.value = [] }
  finally { loading.value = false }
}

const goToDetail = (item: any) => {
  const pathMap: Record<string, string> = { blog: '/blog', news: '/news', product: '/products', solution: '/solutions' }
  router.push(`${pathMap[item.content_type] || '/blog'}/${item.content_id}`)
}

const handleClear = async () => {
  try {
    await ElMessageBox.confirm('确定清空所有阅读历史？', '清空确认', { type: 'warning' })
    await historyApi.clear()
    ElMessage.success('已清空')
    await fetchHistory()
  } catch {}
}

const formatTime = (d: string) => {
  if (!d) return ''
  const diff = Date.now() - new Date(d).getTime()
  const m = Math.floor(diff / 60000)
  if (m < 60) return `${m}分钟前`
  const h = Math.floor(m / 60)
  if (h < 24) return `${h}小时前`
  return new Date(d).toLocaleDateString('zh-CN')
}

onMounted(fetchHistory)
</script>

<style scoped>
.history-view { min-height: 100vh; background: var(--app-bg); padding: 40px 0; }
.container { max-width: 800px; margin: 0 auto; padding: 0 20px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.page-header h1 { margin: 0; }
.loading-state { text-align: center; padding: 80px; color: var(--app-text-secondary); }

.history-list { display: flex; flex-direction: column; gap: 2px; }
.history-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  background: var(--app-bg-card);
  border: 1px solid var(--app-border);
  border-radius: 8px;
  cursor: pointer;
  transition: border-color 0.2s;
}
.history-item:hover { border-color: var(--cyber-neon); }
.history-info { flex: 1; }
.history-info h4 { font-size: 14px; margin: 0 0 2px; color: var(--app-text); }
.history-time { font-size: 12px; color: var(--app-text-secondary); }
.pagination { margin-top: 24px; justify-content: center; }
</style>
