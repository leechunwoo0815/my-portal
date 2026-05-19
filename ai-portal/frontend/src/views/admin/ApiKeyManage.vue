<template>
  <div class="manage-view">
    <div class="page-header">
      <h2>API密钥管理</h2>
      <el-button type="primary" @click="openCreate">
        <el-icon><Plus /></el-icon>新增配置
      </el-button>
    </div>

    <div v-if="list.length === 0 && !loading" class="empty-tip">
      <el-empty description="暂无API密钥配置，请添加服务商配置以开始使用AI对话功能" />
    </div>

    <el-table v-else :data="list" v-loading="loading" style="width:100%">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="provider" label="服务商" width="120">
        <template #default="s">
          <el-tag size="small">{{ s.row.provider }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="模型列表" min-width="220">
        <template #default="s">
          <div class="model-tags">
            <el-tag v-for="m in getModelList(s.row.model_names)" :key="m" size="small" type="info">{{ m }}</el-tag>
            <span v-if="!getModelList(s.row.model_names).length" class="no-model">未配置</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="API密钥" width="200">
        <template #default="s">
          <span v-if="s.row.showKey">{{ s.row.api_key_encrypted }}</span>
          <el-button v-else size="small" link @click="s.row.showKey = true">显示密钥</el-button>
        </template>
      </el-table-column>
      <el-table-column prop="base_url" label="Base URL" min-width="180" show-overflow-tooltip />
      <el-table-column prop="priority" label="优先级" width="80" />
      <el-table-column prop="is_active" label="状态" width="80">
        <template #default="s">
          <el-tag :type="s.row.is_active ? 'success' : 'info'" size="small">
            {{ s.row.is_active ? '启用' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="s">
          <el-button size="small" @click="openEdit(s.row)">编辑</el-button>
          <el-button size="small" type="danger" @click="handleDelete(s.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 新增/编辑对话框 -->
    <el-dialog
      :title="isEdit ? '编辑API配置' : '新增API配置'"
      v-model="visible"
      width="620px"
      destroy-on-close
    >
      <el-form :model="form" label-width="90px">

        <!-- 服务商选择 -->
        <el-form-item label="服务商" required>
          <el-select
            v-model="form.provider"
            placeholder="请选择服务商"
            style="width: 100%"
            :disabled="isEdit"
            @change="onProviderChange"
          >
            <el-option
              v-for="p in PROVIDERS"
              :key="p.id"
              :label="p.name"
              :value="p.id"
            />
          </el-select>
        </el-form-item>

        <!-- API密钥 -->
        <el-form-item label="API密钥" required>
          <el-input
            v-model="form.api_key"
            type="password"
            show-password
            :placeholder="isEdit ? '留空则保持不变' : '请输入API密钥'"
          />
          <div v-if="isEdit" class="form-tip">留空则保持原有密钥不变</div>
        </el-form-item>

        <!-- Base URL -->
        <el-form-item label="Base URL" required>
          <el-input
            v-model="form.base_url"
            placeholder="API接口地址"
          />
          <div class="form-tip">选择服务商后可自动填充，也支持手动修改</div>
        </el-form-item>

        <!-- 模型列表 + 获取按钮 -->
        <el-form-item label="模型列表">
          <div class="model-select-area">
            <div class="model-tags-edit">
              <el-tag
                v-for="m in form.model_names"
                :key="m"
                closable
                size="small"
                type="info"
                @close="removeModel(m)"
              >
                {{ m }}
              </el-tag>
              <span v-if="!form.model_names.length" class="no-model">暂未选择模型</span>
            </div>
            <el-button
              size="small"
              :loading="fetchingModels"
              :disabled="!form.api_key || !form.base_url"
              @click="fetchRemoteModels"
            >
              <el-icon><Refresh /></el-icon>
              从API获取模型
            </el-button>
          </div>
        </el-form-item>

        <!-- 优先级 -->
        <el-form-item label="优先级">
          <el-input-number v-model="form.priority" :min="0" :max="100" />
          <div class="form-tip">数字越大优先级越高，聊天时优先使用</div>
        </el-form-item>

      </el-form>

      <template #footer>
        <el-button @click="visible = false">取消</el-button>
        <el-button type="primary" @click="handleSave" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh } from '@element-plus/icons-vue'
import { getApiKeys, createApiKey, updateApiKey, deleteApiKey, fetchModelsFromApi } from '@/api/admin'

const PROVIDERS = [
  {
    id: 'deepseek',
    name: 'DeepSeek',
    baseUrl: 'https://api.deepseek.com',
    docsUrl: 'https://api-docs.deepseek.com/',
    modelsUrl: 'https://api.deepseek.com/models',
  },
  {
    id: 'openai',
    name: 'OpenAI',
    baseUrl: 'https://api.openai.com/v1',
    docsUrl: 'https://platform.openai.com/docs/',
    modelsUrl: 'https://api.openai.com/v1/models',
  },
  {
    id: 'azure',
    name: 'Azure OpenAI',
    baseUrl: 'https://YOUR_RESOURCE.openai.azure.com',
    docsUrl: 'https://learn.microsoft.com/azure/ai-services/openai/',
    modelsUrl: '',
  },
  {
    id: 'zhipu',
    name: '智谱 GLM',
    baseUrl: 'https://open.bigmodel.cn/api/paas/v4',
    docsUrl: 'https://open.bigmodel.cn/dev/api/',
    modelsUrl: 'https://open.bigmodel.cn/api/paas/v4/models',
  },
  {
    id: 'qwen',
    name: '阿里通义千问',
    baseUrl: 'https://dashscope.aliyuncs.com/compatible-mode/v1',
    docsUrl: 'https://help.aliyun.com/zh/model-studio/',
    modelsUrl: 'https://dashscope.aliyuncs.com/api/v1/models',
  },
  {
    id: 'doubao',
    name: '字节豆包',
    baseUrl: 'https://ark.cn-beijing.volces.com/api/v3',
    docsUrl: 'https://www.volcengine.com/product/doubao',
    modelsUrl: 'https://ark.cn-beijing.volces.com/api/v3/models',
  },
  {
    id: 'silicon',
    name: 'SiliconFlow',
    baseUrl: 'https://api.siliconflow.cn/v1',
    docsUrl: 'https://docs.siliconflow.cn/',
    modelsUrl: 'https://api.siliconflow.cn/v1/models',
  },
  {
    id: 'gemini',
    name: 'Google Gemini',
    baseUrl: 'https://generativelanguage.googleapis.com/v1beta',
    docsUrl: 'https://ai.google.dev/gemini-api/docs',
    modelsUrl: 'https://generativelanguage.googleapis.com/v1beta/models',
  },
  {
    id: 'ollama',
    name: 'Ollama (本地)',
    baseUrl: 'http://localhost:11434/v1',
    docsUrl: 'https://github.com/ollama/ollama/blob/main/docs/api.md',
    modelsUrl: 'http://localhost:11434/api/tags',
  },
  {
    id: 'anthropic',
    name: 'Anthropic Claude',
    baseUrl: 'https://api.anthropic.com/v1',
    docsUrl: 'https://docs.anthropic.com/',
    modelsUrl: 'https://api.anthropic.com/v1/models',
  },
  {
    id: 'other',
    name: '其他自定义',
    baseUrl: '',
    docsUrl: '',
    modelsUrl: '',
  },
]

const list = ref<any[]>([])
const loading = ref(false)
const visible = ref(false)
const saving = ref(false)
const isEdit = ref(false)
const fetchingModels = ref(false)

const form = reactive<any>({
  id: undefined,
  provider: '',
  api_key: '',
  base_url: '',
  model_names: [] as string[],
  priority: 10,
})

const getModelList = (names: any): string[] => {
  if (!names) return []
  if (Array.isArray(names)) return names
  if (typeof names === 'string') return names.split(',').map((s: string) => s.trim()).filter(Boolean)
  return []
}

const onProviderChange = (providerId: string) => {
  const p = PROVIDERS.find(x => x.id === providerId)
  if (p && p.baseUrl) {
    form.base_url = p.baseUrl
  }
}

const removeModel = (m: string) => {
  form.model_names = form.model_names.filter((x: string) => x !== m)
}

const fetchRemoteModels = async () => {
  if (!form.api_key || !form.base_url || !form.provider) {
    ElMessage.warning('请先填写API密钥和Base URL')
    return
  }
  fetchingModels.value = true
  try {
    const res: any = await fetchModelsFromApi(form.api_key, form.base_url, form.provider)
    const models: string[] = res?.models || []
    if (models.length === 0) {
      ElMessage.warning('未获取到模型列表，请确认API密钥和URL是否正确')
      return
    }
    form.model_names = [...new Set([...form.model_names, ...models])]
    ElMessage.success(`成功获取 ${models.length} 个模型`)
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || e?.message || '获取模型列表失败')
  } finally {
    fetchingModels.value = false
  }
}

const fetchList = async () => {
  loading.value = true
  try {
    const res: any = await getApiKeys()
    const data = Array.isArray(res) ? res : (res.data || res || [])
    list.value = data.map((k: any) => ({ ...k, showKey: false }))
  } catch (e) {
    console.error(e)
    list.value = []
  } finally {
    loading.value = false
  }
}

const openCreate = () => {
  form.id = undefined
  form.provider = ''
  form.api_key = ''
  form.base_url = ''
  form.model_names = []
  form.priority = 10
  isEdit.value = false
  visible.value = true
}

const openEdit = (row: any) => {
  form.id = row.id
  form.provider = row.provider
  form.api_key = ''
  form.base_url = row.base_url || ''
  form.model_names = getModelList(row.model_names)
  form.priority = row.priority ?? 10
  isEdit.value = true
  visible.value = true
}

const handleSave = async () => {
  if (!form.provider) {
    ElMessage.warning('请选择服务商')
    return
  }
  if (!form.api_key && !isEdit.value) {
    ElMessage.warning('请填写API密钥')
    return
  }
  if (!form.base_url) {
    ElMessage.warning('请填写Base URL')
    return
  }

  saving.value = true
  try {
    const payload: any = {
      provider: form.provider,
      base_url: form.base_url,
      model_names: form.model_names,
      priority: form.priority,
    }
    if (form.api_key) {
      payload.api_key = form.api_key
    }

    if (isEdit.value && form.id) {
      await updateApiKey(form.id, payload)
      ElMessage.success('更新成功')
    } else {
      await createApiKey(payload)
      ElMessage.success('添加成功')
    }
    visible.value = false
    await fetchList()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || e?.message || '操作失败')
  } finally {
    saving.value = false
  }
}

const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm('确定删除此API配置？', '提示', { type: 'warning' })
    await deleteApiKey(row.id)
    ElMessage.success('删除成功')
    await     fetchList()
  } catch (e) { console.error(e); ElMessage.error('删除失败') }
}

onMounted(fetchList)
</script>

<style scoped>
.manage-view { padding: 20px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.empty-tip { margin-top: 40px; }

.model-tags { display: flex; flex-wrap: wrap; gap: 4px; }
.model-tags .el-tag { margin: 2px; }
.no-model { font-size: 0.8rem; color: var(--app-text-secondary); }

.form-tip { font-size: 0.75rem; color: var(--app-text-secondary); margin-top: 4px; }

.model-select-area { width: 100%; }
.model-tags-edit { display: flex; flex-wrap: wrap; gap: 4px; margin-bottom: 8px; min-height: 28px; }
.model-tags-edit .el-tag { margin: 2px; }
</style>
