<template>
  <div class="config-manage">
    <h3>系统配置</h3>
    <el-table :data="configs" v-loading="loading" stripe>
      <el-table-column prop="key" label="配置键" width="250" />
      <el-table-column prop="value" label="配置值" min-width="200" show-overflow-tooltip />
      <el-table-column prop="description" label="说明" min-width="200" />
      <el-table-column label="操作" width="120">
        <template #default="{ row }">
          <el-button size="small" @click="editConfig(row)">编辑</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="editVisible" title="编辑配置" width="500px">
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="配置键">
          <el-input v-model="editForm.key" disabled />
        </el-form-item>
        <el-form-item label="说明">
          <el-input v-model="editForm.description" disabled />
        </el-form-item>
        <el-form-item label="配置值">
          <el-input v-model="editForm.value" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editVisible = false">取消</el-button>
        <el-button type="primary" @click="saveConfig">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/api/client'

const configs = ref<any[]>([])
const loading = ref(false)
const editVisible = ref(false)
const editForm = reactive({ key: '', value: '', description: '' })

const loadConfigs = async () => {
  loading.value = true
  try {
    const res: any = await api.get('/v1/admin/configs')
    configs.value = Array.isArray(res) ? res : []
  } finally {
    loading.value = false
  }
}

const editConfig = (row: any) => {
  Object.assign(editForm, { key: row.key, value: row.value, description: row.description || '' })
  editVisible.value = true
}

const saveConfig = async () => {
  try {
    await api.put(`/v1/admin/configs/${editForm.key}`, { value: editForm.value })
    ElMessage.success('保存成功')
    editVisible.value = false
    await loadConfigs()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || e?.response?.data?.message || '保存失败')
  }
}

onMounted(loadConfigs)
</script>

<style scoped>
.config-manage { padding: 20px; }
.config-manage h3 { margin-bottom: 16px; }
</style>
