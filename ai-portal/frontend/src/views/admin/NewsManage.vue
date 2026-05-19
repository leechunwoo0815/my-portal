<template>
  <div class="manage-view">
    <div class="page-header">
      <h2>新闻管理</h2>
      <el-button type="primary" @click="openCreate">
        <el-icon><Plus /></el-icon>新增
      </el-button>
    </div>
    <el-table :data="list" :row-key="(row: any) => row.id" v-loading="loading" style="width:100%">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="title" label="标题" min-width="200" show-overflow-tooltip />
      <el-table-column prop="category" label="分类" width="100" />
      <el-table-column prop="tags" label="标签" width="200">
        <template #default="s">
          <el-tag v-for="t in (s.row.tags||'').split(',').filter(Boolean)" :key="t" size="small" style="margin:2px">{{t.trim()}}</el-tag>
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
          <el-popconfirm title="确定删除这条新闻？" confirm-button-text="确定" cancel-button-text="取消" @confirm="handleDelete(s.row.id)">
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
        @size-change="handlePageChange"
        @current-change="handlePageChange"
      />
    </div>
    <el-dialog :title="isEdit?'编辑新闻':'新增新闻'" v-model="dialogVisible" width="90vw" top="5vh" :close-on-click-modal="false">
      <el-form :model="form" label-width="80px">
        <el-form-item label="标题"><el-input v-model="form.title" placeholder="请输入标题" /></el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="分类">
              <el-select v-model="form.category" filterable allow-create default-first-option placeholder="请选择或输入分类" style="width:100%">
                <el-option v-for="item in categoryOptions" :key="item" :label="item" :value="item" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="标签">
              <el-select v-model="form.tagsArray" multiple filterable allow-create default-first-option placeholder="请选择或输入标签" style="width:100%">
                <el-option v-for="item in tagOptions" :key="item" :label="item" :value="item" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="摘要"><el-input v-model="form.summary" type="textarea" :rows="3" placeholder="请输入摘要" /></el-form-item>
        <el-form-item label="内容">
          <MilkdownEditor v-model="form.content" module="news" />
        </el-form-item>
        <el-form-item label="封面图"><CoverUpload v-model="form.cover_image" module="news" /></el-form-item>
        <el-form-item label="状态"><el-switch v-model="form.is_published" /></el-form-item>
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
import { adminListNews, createNews, updateNews, deleteNews } from '@/api/news'
import { useCrudAdmin } from '@/composables/useCrudAdmin'
import MilkdownEditor from '@/components/editor/MilkdownEditor.vue'
import CoverUpload from '@/components/CoverUpload.vue'

const categoryOptions = ref<string[]>([])
const tagOptions = ref<string[]>([])

const {
  list, loading, total, page, pageSize,
  dialogVisible, saving, isEdit, form,
  formatDate, fetchList, openCreate, openEdit, handleSave, handleDelete, handlePageChange,
} = useCrudAdmin({
  fetchList: (params) => adminListNews(params),
  createItem: (data) => createNews(data),
  updateItem: (id, data) => updateNews(id, data),
  deleteItem: (id) => deleteNews(id),
  defaultForm: () => ({ id: undefined, title: '', summary: '', content: '', content_type: 'markdown', cover_image: '', category: '', tags: '', tagsArray: [], is_published: false }),
  deleteConfirmMessage: '确定删除这条新闻？',
  entityName: '新闻',
})

onMounted(fetchList)
</script>

<style scoped>
.manage-view { padding: 20px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
</style>
