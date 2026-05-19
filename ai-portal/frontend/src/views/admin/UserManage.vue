<template>
  <div class="user-manage">
    <div class="toolbar">
      <el-input v-model="keyword" placeholder="搜索用户名/邮箱" clearable @clear="loadUsers" @keyup.enter="loadUsers" style="width:300px" />
      <el-button type="primary" @click="loadUsers">搜索</el-button>
      <el-button type="success" @click="openCreate">新增用户</el-button>
    </div>

    <el-table :data="users" v-loading="loading" stripe>
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column label="用户" min-width="150">
        <template #default="{ row }">
          <div style="display:flex;align-items:center;gap:8px">
            <el-avatar :size="32" :src="row.avatar_url">{{ row.username?.charAt(0) }}</el-avatar>
            <div>
              <div>{{ row.nickname || row.username }}</div>
              <div style="font-size:12px;color:#999">@{{ row.username }}</div>
            </div>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="email" label="邮箱" width="180" />
      <el-table-column label="等级" width="80">
        <template #default="{ row }">
          <el-tag size="small" :type="row.level === 999 ? 'success' : 'info'">
            {{ row.level === 999 ? '管理员' : `LV${row.level}` }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="points" label="积分" width="80" />
      <el-table-column label="评论数" width="100" align="center">
        <template #default="{ row }">
          <el-link type="primary" @click="viewUserComments(row)">{{ row.comment_count || 0 }}</el-link>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="80">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
            {{ row.is_active ? '正常' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="250">
        <template #default="{ row }">
          <el-button size="small" @click="editUser(row)">编辑</el-button>
          <el-button size="small" @click="viewUserComments(row)">查看评论</el-button>
          <el-popconfirm title="确定删除?" @confirm="deleteUser(row.id)">
            <template #reference>
              <el-button size="small" type="danger">删除</el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination v-model:current-page="page" :page-size="20" :total="total" layout="prev, pager, next" @current-change="loadUsers" style="margin-top:16px" />

    <el-dialog v-model="createVisible" title="新增用户" width="500px">
      <el-form :model="createForm" label-width="80px">
        <el-form-item label="用户名"><el-input v-model="createForm.username" placeholder="3-50位" /></el-form-item>
        <el-form-item label="邮箱"><el-input v-model="createForm.email" placeholder="user@example.com" /></el-form-item>
        <el-form-item label="密码"><el-input v-model="createForm.password" type="password" placeholder="至少6位" /></el-form-item>
        <el-form-item label="昵称"><el-input v-model="createForm.nickname" placeholder="选填" /></el-form-item>
        <el-form-item label="等级"><el-input-number v-model="createForm.level" :min="1" :max="999" /></el-form-item>
        <el-form-item label="管理员">
          <el-switch v-model="createForm.is_admin" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createVisible = false">取消</el-button>
        <el-button type="primary" @click="doCreateUser" :loading="createLoading">创建</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="editVisible" title="编辑用户" width="500px">
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="昵称"><el-input v-model="editForm.nickname" /></el-form-item>
        <el-form-item label="等级"><el-input-number v-model="editForm.level" :min="1" :max="999" /></el-form-item>
        <el-form-item label="积分"><el-input-number v-model="editForm.points" :min="0" /></el-form-item>
        <el-form-item label="管理员">
          <el-switch v-model="editForm.is_admin" />
        </el-form-item>
        <el-form-item label="启用">
          <el-switch v-model="editForm.is_active" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editVisible = false">取消</el-button>
        <el-button type="primary" @click="saveUser">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '@/api/client'

const router = useRouter()
const route = useRoute()
const users = ref<any[]>([])
const loading = ref(false)
const keyword = ref('')
const page = ref(1)
const total = ref(0)
const createVisible = ref(false)
const createLoading = ref(false)
const createForm = reactive({ username: '', email: '', password: '', nickname: '', level: 1, is_admin: false })
const editVisible = ref(false)
const editForm = reactive({ id: 0, nickname: '', level: 1, points: 0, is_admin: false, is_active: true })

const loadUsers = async () => {
  loading.value = true
  try {
    const res: any = await api.get('/v1/admin/users', { params: { page: page.value, keyword: keyword.value } })
    users.value = res.items || []
    total.value = res.total || 0
  } finally {
    loading.value = false
  }
}

const openCreate = () => {
  Object.assign(createForm, { username: '', email: '', password: '', nickname: '', level: 1, is_admin: false })
  createVisible.value = true
}

const doCreateUser = async () => {
  if (!createForm.username.trim() || !createForm.email.trim() || !createForm.password.trim()) {
    ElMessage.warning('请填写完整信息')
    return
  }
  createLoading.value = true
  try {
    await api.post('/v1/admin/users', {
      username: createForm.username.trim(),
      email: createForm.email.trim(),
      password: createForm.password,
      nickname: createForm.nickname.trim() || undefined,
      level: createForm.level,
      is_admin: createForm.is_admin,
    })
    ElMessage.success('创建成功')
    createVisible.value = false
    await loadUsers()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || e?.response?.data?.message || '创建失败')
  } finally { createLoading.value = false }
}

const editUser = (row: any) => {
  Object.assign(editForm, { id: row.id, nickname: row.nickname, level: row.level, points: row.points, is_admin: row.is_admin, is_active: row.is_active })
  editVisible.value = true
}

const saveUser = async () => {
  try {
    await api.put(`/v1/admin/users/${editForm.id}`, {
      nickname: editForm.nickname, level: editForm.level, points: editForm.points,
      is_admin: editForm.is_admin, is_active: editForm.is_active,
    })
    ElMessage.success('保存成功')
    editVisible.value = false
    await loadUsers()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '保存失败')
  }
}

const deleteUser = async (id: number) => {
  try {
    await api.delete(`/v1/admin/users/${id}`)
    ElMessage.success('删除成功')
    await loadUsers()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '删除失败')
  }
}

const viewUserComments = (user: any) => {
  router.push(`/admin/comments?user_id=${user.id}`)
}

onMounted(loadUsers)
</script>

<style scoped>
.toolbar { display: flex; gap: 12px; margin-bottom: 16px; }
</style>
