<template>
  <div class="manage-view">
    <div class="page-header">
      <h2>知识库管理</h2>
      <el-button type="primary" @click="openCreate"><el-icon><Plus /></el-icon>新增</el-button>
    </div>
    <el-table :data="list" v-loading="loading" style="width:100%">
      <el-table-column type="expand">
        <template #default="s">
          <div style="padding:12px 20px">
            <div style="margin-bottom:8px;font-weight:500">文档列表</div>
            <el-table :data="s.row.documents||[]" size="small" stripe>
              <el-table-column prop="id" label="ID" width="50" />
              <el-table-column prop="filename" label="文件名" min-width="200" />
              <el-table-column prop="file_type" label="类型" width="70" />
              <el-table-column prop="file_size" label="大小" width="100">
                <template #default="d">{{ (d.row.file_size/1024).toFixed(1) }} KB</template>
              </el-table-column>
              <el-table-column prop="chunk_count" label="分块数" width="70" align="right" />
              <el-table-column prop="created_at" label="上传时间" width="150" />
              <el-table-column label="操作" width="80">
                <template #default="d"><el-button size="small" type="danger" link @click="deleteDoc(s.row.id,d.row.id)">删除</el-button></template>
              </el-table-column>
            </el-table>
            <div v-if="!s.row.documents||s.row.documents.length===0" style="color:#999;padding:12px">暂无文档</div>
            <el-upload :action="`/api/v1/knowledge/bases/${s.row.id}/documents`" :headers="{Authorization:'Bearer '+(authToken)}" :show-file-list="false" :on-success="()=>fetchList()" style="margin-top:8px">
              <el-button size="small" type="primary">上传文档</el-button>
            </el-upload>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="name" label="名称" min-width="160" />
      <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
      <el-table-column prop="embedding_model" label="嵌入模型" width="140" />
      <el-table-column label="文档数" width="80" align="right">
        <template #default="s">{{ (s.row.documents||[]).length }}</template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="150" />
      <el-table-column label="操作" width="160" fixed="right">
        <template #default="s">
          <el-button size="small" @click="openEdit(s.row)">编辑</el-button>
          <el-button size="small" type="danger" @click="handleDelete(s.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-dialog :title="isEdit?'编辑知识库':'新增知识库'" v-model="visible" width="500px" destroy-on-close>
      <el-form :model="form" label-width="90px">
        <el-form-item label="名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="form.description" type="textarea" :rows="3" /></el-form-item>
        <el-form-item label="嵌入模型"><el-select v-model="form.embedding_model" style="width:100%">
          <el-option label="text-embedding-3-small (默认)" value="" />
          <el-option label="text-embedding-ada-002" value="text-embedding-ada-002" />
        </el-select></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="visible=false">取消</el-button>
        <el-button type="primary" @click="handleSave" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { getKnowledgeBases, createKnowledgeBase, updateKnowledgeBase, deleteKnowledgeBase, deleteDocument } from '@/api/knowledge'

const list = ref<any[]>([])
const loading = ref(false)
const visible = ref(false)
const saving = ref(false)
const isEdit = ref(false)
const form = ref<any>({ name:'', description:'', embedding_model:'', id:undefined })
const authToken = ref('')

const fetchList = async () => {
  loading.value = true
  try {
    const res = await getKnowledgeBases()
    const data = Array.isArray(res) ? res : (res.data || res || [])
    list.value = data
  } catch (e) { console.error(e); list.value = [] }
  finally { loading.value = false }
}
const openCreate = () => {
  form.value = { name:'', description:'', embedding_model:'', id:undefined }
  isEdit.value = false; visible.value = true
}
const openEdit = (row: any) => {
  form.value = { name: row.name, description: row.description, embedding_model: row.embedding_model || '', id: row.id }
  isEdit.value = true; visible.value = true
}
const handleSave = async () => {
  saving.value = true
  try {
    const payload: any = { ...form.value }
    if (!payload.embedding_model) delete payload.embedding_model
    delete payload.id
    if (isEdit.value && form.value.id) {
      await updateKnowledgeBase(form.value.id, payload)
      ElMessage.success('更新成功')
    } else {
      await createKnowledgeBase(payload)
      ElMessage.success('创建成功')
    }
    visible.value = false; await fetchList()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || e?.message || '操作失败')
  } finally { saving.value = false }
}
const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm(`确定删除"${row.name}"？`, '提示', { type: 'warning' })
    await deleteKnowledgeBase(row.id)
    ElMessage.success('删除成功'); await fetchList()
  } catch (e) { console.error(e); ElMessage.error('删除失败') }
}
const deleteDoc = async (kbId: number, docId: number) => {
  try {
    await ElMessageBox.confirm('确定删除此文档？', '提示', { type: 'warning' })
    await deleteDocument(kbId, docId)
    ElMessage.success('文档已删除'); await fetchList()
  } catch (e) { console.error(e); ElMessage.error('删除失败') }
}

onMounted(() => {
  authToken.value = localStorage.getItem('access_token') || ''
  fetchList()
})
</script>
<style scoped>
.manage-view { padding: 20px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
</style>
