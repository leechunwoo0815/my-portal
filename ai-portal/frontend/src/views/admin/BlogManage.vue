<template>
  <div class="manage-view">
    <div class="page-header">
      <h2>博客管理</h2>
      <div class="toolbar">
        <el-select v-model="filterAuthorId" placeholder="按作者筛选" clearable @change="onAuthorFilterChange" style="width:200px">
          <el-option v-for="u in userOptions" :key="u.id" :label="u.nickname || u.username" :value="u.id" />
        </el-select>
        <el-button type="primary" @click="openCreate">
          <el-icon><Plus /></el-icon>新增
        </el-button>
      </div>
    </div>
    <el-table :data="list" v-loading="loading" style="width:100%">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column label="作者" width="120">
        <template #default="{ row }">
          <div style="display:flex;align-items:center;gap:6px" v-if="row.author">
            <el-avatar :size="24" :src="row.author.avatar_url">{{ row.author.username?.charAt(0) }}</el-avatar>
            <span>{{ row.author.nickname || row.author.username }}</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="title" label="标题" min-width="200" show-overflow-tooltip />
      <el-table-column prop="category" label="分类" width="100" />
      <el-table-column label="标签" width="160">
        <template #default="s">
          <el-tag size="small" v-for="t in (Array.isArray(s.row.tags) ? s.row.tags : (typeof s.row.tags === 'string' ? s.row.tags.split(',') : [])).filter(Boolean)" :key="t" style="margin:2px">{{t}}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="80">
        <template #default="s"><el-tag :type="s.row.is_published?'success':'info'">{{s.row.is_published?'已发布':'草稿'}}</el-tag></template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="160">
        <template #default="s"><span>{{ formatDate(s.row.created_at) }}</span></template>
      </el-table-column>
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="s">
          <el-button size="small" @click="openEdit(s.row)">编辑</el-button>
          <el-popconfirm title="确定删除这篇博客？" confirm-button-text="确定" cancel-button-text="取消" @confirm="handleDelete(s.row.id)">
            <template #reference>
              <el-button size="small" type="danger">删除</el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>
    <el-dialog :title="isEdit?'编辑博客':'新增博客'" v-model="dialogVisible" width="90vw" top="5vh" :close-on-click-modal="false">
      <el-form :model="form" label-width="70px">
        <el-form-item label="标题"><el-input v-model="form.title" /></el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="分类">
              <el-select v-model="form.category" filterable allow-create default-first-option placeholder="请选择或输入分类" style="width: 100%">
                <el-option v-for="item in categoryOptions" :key="item" :label="item" :value="item" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="标签">
              <el-select v-model="form.tagsArray" multiple filterable allow-create default-first-option placeholder="请选择或输入标签" style="width: 100%">
                <el-option v-for="item in tagOptions" :key="item" :label="item" :value="item" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="摘要"><el-input v-model="form.summary" type="textarea" :rows="2" /></el-form-item>
        <el-form-item label="封面"><CoverUpload v-model="form.cover_image" module="blog" /></el-form-item>
        <el-form-item label="内容">
          <MilkdownEditor v-model="form.content" module="blog" />
        </el-form-item>
        <el-form-item label="发布"><el-switch v-model="form.is_published" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible=false">取消</el-button>
        <el-button type="primary" @click="handleSave()" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { adminListBlogs, createBlog, updateBlog, deleteBlog } from '@/api/blog'
import { useCrudAdmin } from '@/composables/useCrudAdmin'
import MilkdownEditor from '@/components/editor/MilkdownEditor.vue'
import CoverUpload from '@/components/CoverUpload.vue'
import api from '@/api/client'

const filterAuthorId = ref<any>(undefined)
const userOptions = ref<any[]>([])
const categoryOptions = ref<string[]>(['前端开发', '后端开发', '人工智能', '机器学习', '架构设计', '运维部署'])
const tagOptions = ref<string[]>(['Vue3', 'React', 'Python', 'FastAPI', 'DeepSeek', 'Docker', 'K8s'])

const {
  list, loading, dialogVisible, saving, isEdit, form,
  formatDate, fetchList, openCreate, openEdit, handleSave, handleDelete,
} = useCrudAdmin({
  fetchList: (params) => adminListBlogs(params),
  createItem: (data) => createBlog(data),
  updateItem: (id, data) => updateBlog(id, data),
  deleteItem: (id) => deleteBlog(id),
  defaultForm: () => ({
    id: undefined, title: '', summary: '', content: '',
    cover_image: '', category: '', tags: '', tagsArray: [], is_published: false,
  }),
  deleteConfirmMessage: '确定删除这篇博客？',
  entityName: '博客',
})

const onAuthorFilterChange = () => {
  const extraParams: any = {}
  if (filterAuthorId.value) extraParams.author_id = filterAuthorId.value
  fetchList(extraParams)
}

const fetchUserOptions = async () => {
  try {
    const res: any = await api.get('/v1/admin/users', { params: { page_size: 100 } })
    userOptions.value = res.items || []
  } catch {}
}

onMounted(() => {
  fetchUserOptions()
  fetchList()
})
</script>

<style scoped>
.manage-view { padding: 20px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.toolbar { display: flex; gap: 12px; }
</style>
