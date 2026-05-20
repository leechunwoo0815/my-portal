<template>
  <el-popover trigger="click" width="300" :visible="visible">
    <template #reference>
      <el-button size="small" text @click="visible = !visible">
        <el-icon><Warning /></el-icon> 举报
      </el-button>
    </template>
    <div class="report-form">
      <p style="font-weight:600;margin-bottom:8px;">举报原因</p>
      <el-radio-group v-model="reason" style="display:flex;flex-direction:column;gap:6px;">
        <el-radio value="spam">垃圾广告</el-radio>
        <el-radio value="abuse">辱骂/骚扰</el-radio>
        <el-radio value="illegal">违法违规</el-radio>
        <el-radio value="other">其他</el-radio>
      </el-radio-group>
      <el-input v-if="reason === 'other'" v-model="description" type="textarea" :rows="2" placeholder="请描述具体原因..." style="margin-top:8px;" />
      <div style="display:flex;justify-content:flex-end;gap:8px;margin-top:12px;">
        <el-button size="small" @click="visible = false">取消</el-button>
        <el-button size="small" type="danger" :disabled="!reason" :loading="submitting" @click="submit">提交举报</el-button>
      </div>
    </div>
  </el-popover>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Warning } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import api from '@/api/client'

const props = defineProps<{
  targetType: string
  targetId: number
}>()

const visible = ref(false)
const reason = ref('')
const description = ref('')
const submitting = ref(false)

const submit = async () => {
  submitting.value = true
  try {
    await api.post('/v1/report/', {
      target_type: props.targetType,
      target_id: props.targetId,
      reason: reason.value,
      description: description.value || null,
    })
    ElMessage.success('举报已提交')
    visible.value = false
    reason.value = ''
    description.value = ''
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '举报失败')
  } finally {
    submitting.value = false
  }
}
</script>
