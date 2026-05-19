<template>
  <div class="series-list-view">
    <div class="container">
      <div class="page-header">
        <h1>专栏</h1>
        <p class="subtitle">系统化的技术知识集合</p>
        <el-button v-if="authStore.isLoggedIn" type="primary" @click="showCreate = true">
          <el-icon><Plus /></el-icon>创建专栏
        </el-button>
      </div>

      <div v-if="loading" class="series-grid">
        <div v-for="i in 6" :key="i" class="series-card-skeleton">
          <div class="skel-cover" />
          <div class="skel-lines">
            <div class="skel-bone w-3-4" />
            <div class="skel-bone w-full" />
            <div class="skel-bone w-1-2" />
          </div>
        </div>
      </div>

      <el-empty v-else-if="seriesList.length === 0" description="暂无专栏">
        <el-button v-if="authStore.isLoggedIn" type="primary" @click="showCreate = true">创建第一个专栏</el-button>
      </el-empty>

      <div v-else class="series-grid">
        <div v-for="s in seriesList" :key="s.id" class="series-card" @click="$router.push(`/series/${s.id}`)">
          <div class="series-cover" v-if="s.cover_image">
            <img :src="s.cover_image" :alt="s.title" />
          </div>
          <div class="series-cover placeholder" v-else>
            <span>📚</span>
          </div>
          <div class="series-info">
            <h3 class="series-title">{{ s.title }}</h3>
            <p class="series-desc">{{ s.description || '暂无描述' }}</p>
            <div class="series-meta">
              <span>{{ s.articles_count || 0 }} 篇文章</span>
              <span>{{ formatDate(s.created_at) }}</span>
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
        @current-change="fetchSeries"
        class="pagination"
      />
    </div>

    <el-dialog v-model="showCreate" title="创建专栏" width="500px" :close-on-click-modal="false">
      <el-form :model="createForm" label-width="80px">
        <el-form-item label="标题" required>
          <el-input v-model="createForm.title" placeholder="专栏标题" maxlength="100" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="createForm.description" type="textarea" :rows="3" placeholder="专栏描述" maxlength="500" />
        </el-form-item>
        <el-form-item label="公开">
          <el-switch v-model="createForm.is_public" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreate = false">取消</el-button>
        <el-button type="primary" :loading="creating" @click="handleCreate">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { seriesApi } from '@/api/series'
import { ElMessage } from 'element-plus'

const authStore = useAuthStore()
const loading = ref(false)
const seriesList = ref<any[]>([])
const page = ref(1)
const pageSize = ref(12)
const total = ref(0)
const showCreate = ref(false)
const creating = ref(false)
const createForm = reactive({ title: '', description: '', is_public: true })

const fetchSeries = async () => {
  loading.value = true
  try {
    const res: any = await seriesApi.list(page.value, pageSize.value)
    seriesList.value = res.items || []
    total.value = res.total || 0
  } catch { seriesList.value = [] }
  finally { loading.value = false }
}

const handleCreate = async () => {
  if (!createForm.title.trim()) return ElMessage.warning('请输入标题')
  creating.value = true
  try {
    await seriesApi.create(createForm)
    ElMessage.success('创建成功')
    showCreate.value = false
    createForm.title = ''
    createForm.description = ''
    await fetchSeries()
  } catch { ElMessage.error('创建失败') }
  finally { creating.value = false }
}

const formatDate = (d: string) => d ? new Date(d).toLocaleDateString('zh-CN') : ''

onMounted(fetchSeries)
</script>

<style scoped>
.series-list-view { min-height: 100vh; background: var(--app-bg); padding: 40px 0; }
.container { max-width: 1200px; margin: 0 auto; padding: 0 20px; }
.page-header { text-align: center; margin-bottom: 40px; }
.page-header h1 { font-size: 2rem; margin-bottom: 8px; }
.subtitle { color: var(--app-text-secondary); margin-bottom: 16px; }

.series-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 20px; }
.series-card {
  background: var(--app-bg-card);
  border: 1px solid var(--app-border);
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.2s;
}
.series-card:hover { border-color: var(--cyber-neon); box-shadow: 0 4px 12px rgba(0, 212, 170, 0.1); transform: translateY(-2px); }
.series-cover { height: 140px; overflow: hidden; }
.series-cover img { width: 100%; height: 100%; object-fit: cover; }
.series-cover.placeholder { display: flex; align-items: center; justify-content: center; background: var(--app-bg); font-size: 48px; }
.series-info { padding: 16px; }
.series-title { font-size: 16px; font-weight: 600; margin: 0 0 8px; color: var(--app-text); }
.series-desc { font-size: 13px; color: var(--app-text-secondary); margin: 0 0 8px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.series-meta { display: flex; gap: 12px; font-size: 12px; color: var(--app-text-secondary); }

.series-card-skeleton {
  background: var(--app-bg-card);
  border: 1px solid var(--app-border);
  border-radius: 12px;
  overflow: hidden;
  animation: skeleton-pulse 1.5s ease-in-out infinite;
}
.skel-cover { height: 140px; background: var(--app-border); }
.skel-lines { padding: 16px; display: flex; flex-direction: column; gap: 8px; }
.skel-bone { height: 14px; border-radius: 4px; background: var(--app-border); }
.w-full { width: 100%; }
.w-3-4 { width: 75%; }
.w-1-2 { width: 50%; }

.pagination { margin-top: 24px; justify-content: center; }

@keyframes skeleton-pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
</style>
