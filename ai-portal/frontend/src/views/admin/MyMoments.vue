<template>
  <div class="moment-manage">
    <div class="page-header">
      <h2>动态管理</h2>
      <div class="toolbar">
        <el-select v-model="filterUserId" placeholder="按用户筛选" clearable @change="loadMoments" style="width:200px">
          <el-option v-for="u in userOptions" :key="u.id" :label="u.nickname || u.username" :value="u.id" />
        </el-select>
      </div>
    </div>

    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="moments.length === 0" class="empty">暂无动态</div>
    <div v-else class="moment-list">
      <el-card v-for="m in moments" :key="m.id" class="moment-card" shadow="hover">
        <div class="moment-head">
          <el-avatar :size="32" :src="m.author?.avatar_url">
            {{ m.author?.username?.charAt(0) }}
          </el-avatar>
          <div class="moment-user">
            <strong>{{ m.author?.nickname || m.author?.username }}</strong>
            <el-tag size="small" :type="m.author?.level === 999 ? 'success' : 'info'" class="lv-tag">
              {{ m.author?.level === 999 ? '管理员' : 'LV' + (m.author?.level || 1) }}
            </el-tag>
          </div>
          <span class="moment-time">{{ formatDate(m.created_at) }}</span>
        </div>
        <div class="moment-body">
          <p>{{ m.content }}</p>
          <div class="moment-images" v-if="m.images && m.images.length">
            <img v-for="img in m.images" :key="img" :src="img" class="moment-img" />
          </div>
        </div>
        <div class="moment-footer">
          <span>❤️ {{ m.likes_count || 0 }}</span>
          <span>💬 {{ m.comments_count || 0 }}</span>
          <el-popconfirm title="确定删除这条动态？" confirm-button-text="确定" cancel-button-text="取消" @confirm="handleDelete(m.id)">
            <template #reference>
              <el-button size="small" type="danger" text>删除</el-button>
            </template>
          </el-popconfirm>
        </div>
      </el-card>
    </div>

    <el-pagination v-if="total > pageSize" v-model:current-page="page" :page-size="pageSize" :total="total" layout="prev, pager, next" @current-change="loadMoments" style="margin-top:16px" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getAdminMoments, deleteAdminMoment } from '@/api/admin'
import api from '@/api/client'

const loading = ref(false)
const moments = ref<any[]>([])
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const filterUserId = ref<number | null>(null)
const userOptions = ref<any[]>([])

const fetchUserOptions = async () => {
  try {
    const res: any = await api.get('/v1/admin/users', { params: { page_size: 100 } })
    userOptions.value = res.items || []
  } catch {}
}

const loadMoments = async () => {
  loading.value = true
  try {
    const params: any = { page: page.value, page_size: pageSize.value }
    if (filterUserId.value) params.user_id = filterUserId.value
    const res: any = await getAdminMoments(params)
    moments.value = res.items || []
    total.value = res.total || 0
  } catch { ElMessage.error('加载失败') }
  finally { loading.value = false }
}

const handleDelete = async (id: number) => {
  try {
    await deleteAdminMoment(id)
    ElMessage.success('已删除')
    await loadMoments()
  } catch { ElMessage.error('删除失败') }
}

const formatDate = (d?: string) => d ? new Date(d).toLocaleString('zh-CN') : ''

onMounted(() => {
  fetchUserOptions()
  loadMoments()
})
</script>

<style scoped>
.moment-manage { padding: 20px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.toolbar { display: flex; gap: 12px; }
.loading, .empty { text-align: center; padding: 40px; color: var(--app-text-secondary); }
.moment-list { display: flex; flex-direction: column; gap: 16px; }
.moment-head { display: flex; align-items: center; gap: 10px; }
.moment-user { flex: 1; }
.moment-time { font-size: 12px; color: var(--app-text-secondary); }
.moment-body { margin: 12px 0; }
.moment-body p { margin: 0; line-height: 1.6; white-space: pre-wrap; }
.moment-images { display: flex; gap: 8px; margin-top: 8px; flex-wrap: wrap; }
.moment-img { width: 120px; height: 120px; object-fit: cover; border-radius: 6px; }
.moment-footer { display: flex; gap: 16px; align-items: center; color: var(--app-text-secondary); font-size: 13px; }
.lv-tag { margin-left: 6px; }
</style>
