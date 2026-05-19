<template>
  <div class="manage-view">
    <div class="page-header">
      <h2>评论管理</h2>
      <div class="toolbar">
        <el-select v-model="filterUserId" placeholder="按用户筛选" clearable @change="fetchList" style="width:200px">
          <el-option v-for="u in userOptions" :key="u.id" :label="u.nickname || u.username" :value="u.id" />
        </el-select>
      </div>
    </div>
    <el-table :data="list" row-key="id" v-loading="loading" style="width:100%">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column label="作者" width="140">
        <template #default="{ row }">
          <div style="display:flex;align-items:center;gap:6px">
            <el-avatar v-if="row.avatar_url" :size="24" :src="row.avatar_url" />
            <span v-else style="font-size:16px">{{ row.emoji || '🙂' }}</span>
            <el-link v-if="row.user_id" type="primary" @click="goToUser(row.user_id)">{{ row.author_name }}</el-link>
            <span v-else>{{ row.author_name }}</span>
            <el-tag size="small" :type="row.level === 999 ? 'success' : 'info'" style="font-size:10px">
              {{ row.level === 999 ? '管理员' : 'LV' + (row.level || 1) }}
            </el-tag>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="来源" width="90">
        <template #default="s">
          <el-tag :type="s.row.target_type === 'blog' ? 'info' : 'danger'" size="small">{{ s.row.target_type === 'blog' ? '博客' : '新闻' }}</el-tag>
          <span style="margin-left:4px;font-size:12px;color:var(--app-text-secondary)">#{{ s.row.target_id }}</span>
        </template>
      </el-table-column>
      <el-table-column label="回复" width="160" show-overflow-tooltip>
        <template #default="s">
          <span v-if="s.row.parent" class="cs-parent">
            @{{ s.row.parent.author_name }}: {{ s.row.parent.content }}
          </span>
          <span v-else class="cs-root-tag">顶级评论</span>
        </template>
      </el-table-column>
      <el-table-column prop="content" label="内容" min-width="240" show-overflow-tooltip />
      <el-table-column prop="likes_count" label="赞" width="60" align="center" />
      <el-table-column prop="created_at" label="时间" width="150">
        <template #default="s">{{ formatDate(s.row.created_at) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="120" fixed="right">
        <template #default="s">
          <el-popconfirm title="将删除此评论及其所有回复，确认？" @confirm="handleDelete(s.row)">
            <template #reference>
              <el-button size="small" type="danger">删除</el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>
    <div style="margin-top:16px;text-align:right">
      <el-pagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="total"
        layout="total, sizes, prev, pager, next"
        background
        @size-change="fetchList"
        @current-change="fetchList"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '@/api/client'

const router = useRouter()
const route = useRoute()
const list = ref<any[]>([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const filterUserId = ref<number | null>(null)
const userOptions = ref<any[]>([])

const formatDate = (d?: string) => d ? new Date(d).toLocaleString('zh-CN') : ''

const goToUser = (userId: number) => {
  router.push(`/admin/users?highlight=${userId}`)
}

const fetchList = async () => {
  loading.value = true
  try {
    const params: any = { page: page.value, page_size: pageSize.value }
    if (filterUserId.value) params.user_id = filterUserId.value
    const res: any = await api.get('/v1/admin/comments', { params })
    total.value = res.total || 0
    list.value = res.items || []
  } catch { ElMessage.error('加载失败') }
  finally { loading.value = false }
}

const fetchUserOptions = async () => {
  try {
    const res: any = await api.get('/v1/admin/users', { params: { page_size: 100 } })
    userOptions.value = res.items || []
  } catch {}
}

const handleDelete = async (row: any) => {
  try {
    const res: any = await api.delete(`/v1/admin/comments/${row.id}`)
    ElMessage.success(res.message || '已删除')
    await fetchList()
  } catch { ElMessage.error('删除失败') }
}

onMounted(() => {
  fetchUserOptions()
  // 从URL参数获取user_id筛选
  const userIdParam = route.query.user_id
  if (userIdParam) {
    filterUserId.value = parseInt(userIdParam as string)
  }
  fetchList()
})
</script>
<style scoped>
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.toolbar { display: flex; gap: 12px; }
.cs-parent { font-size: 12px; color: var(--app-text-secondary); }
.cs-root-tag { font-size: 12px; color: var(--el-color-success); }
</style>