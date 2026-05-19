<template>
  <div class="manage-view">
    <div class="page-header"><h2>API调用日志</h2></div>
    <el-card shadow="never">
      <el-form :inline="true" class="filter-form">
        <el-form-item label="提供商"><el-input v-model="filters.provider" placeholder="筛选" clearable style="width:140px" /></el-form-item>
        <el-form-item label="模型"><el-input v-model="filters.model_name" placeholder="筛选" clearable style="width:160px" /></el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchList">查询</el-button>
          <el-button @click="filters={provider:'',model_name:''};fetchList()">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    <el-table :data="list" v-loading="loading" style="width:100%;margin-top:16px" stripe>
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="provider" label="提供商" width="90" />
      <el-table-column prop="model_name" label="模型" width="140" show-overflow-tooltip />
      <el-table-column prop="endpoint" label="接口" min-width="200" show-overflow-tooltip />
      <el-table-column label="状态码" width="80">
        <template #default="s"><el-tag :type="s.row.status_code<300?'success':'danger'" size="small">{{s.row.status_code}}</el-tag></template>
      </el-table-column>
      <el-table-column prop="prompt_tokens" label="输入Token" width="90" align="right" />
      <el-table-column prop="completion_tokens" label="输出Token" width="90" align="right" />
      <el-table-column prop="total_tokens" label="总Token" width="90" align="right" />
      <el-table-column prop="duration_ms" label="耗时(ms)" width="90" align="right" />
      <el-table-column prop="created_at" label="时间" width="160" />
      <el-table-column label="操作" width="80" fixed="right">
        <template #default="s">
          <el-button size="small" link @click="showDetail(s.row)">详情</el-button>
        </template>
      </el-table-column>
    </el-table>
    <div style="text-align:right;margin-top:16px">
      <el-pagination v-if="total>0" background layout="prev,pager,next,total" :total="total" :page-size="pageSize" v-model:current-page="page" @current-change="fetchList" />
    </div>
    <el-dialog v-model="detailVisible" title="请求详情" width="700px">
      <pre style="max-height:400px;overflow:auto;background:#1a1a2e;color:#e0e0e0;padding:16px;border-radius:6px;font-size:13px">{{detailData}}</pre>
    </el-dialog>
  </div>
</template>
<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { getApiLogs } from '@/api/admin'

const list = ref<any[]>([])
const loading = ref(false)
const total = ref(0)
const page = ref(1)
const pageSize = 20
const filters = reactive({ provider:'', model_name:'' })
const detailVisible = ref(false)
const detailData = ref('')

const fetchList = async () => {
  loading.value = true
  try {
    const res = await getApiLogs({ page: page.value, page_size: pageSize, ...filters })
    const data: any = (res as any).items || (res as any).data || res || { items: [], total: 0 }
    list.value = Array.isArray(data) ? data : (data.items || [])
    total.value = data.total || list.value.length
  } catch { list.value = []; total.value = 0 }
  finally { loading.value = false }
}
const showDetail = (row: any) => {
  let requestData = null
  let responseData = null
  try {
    requestData = row.request_body ? (typeof row.request_body === 'string' ? JSON.parse(row.request_body) : row.request_body) : null
  } catch { requestData = row.request_body }
  try {
    responseData = row.response_body ? (typeof row.response_body === 'string' ? JSON.parse(row.response_body) : row.response_body) : null
  } catch { responseData = row.response_body }
  detailData.value = JSON.stringify({
    request: requestData,
    response: responseData,
    error: row.error_message || null,
    endpoint: row.endpoint,
    provider: row.provider,
    model: row.model_name,
  }, null, 2)
  detailVisible.value = true
}
onMounted(fetchList)
</script>
<style scoped>
.manage-view { padding: 20px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; }
.filter-form { margin-bottom: 0; }
pre { white-space: pre-wrap; word-break: break-all; }
</style>
