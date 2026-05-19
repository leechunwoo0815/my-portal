<template>
  <div class="cover-upload">
    <el-input :model-value="modelValue" placeholder="图片URL或上传本地图片" @input="$emit('update:modelValue', $event)" />
    <div class="cover-actions">
      <el-upload
        :before-upload="beforeUpload"
        :http-request="handleRequest"
        accept="image/*"
        :show-file-list="false"
      >
        <el-button size="small" type="primary">本地上传</el-button>
      </el-upload>
      <el-button v-if="modelValue" size="small" type="info" @click="previewVisible = !previewVisible">
        {{ previewVisible ? '收起' : '预览' }}
      </el-button>
    </div>
    <div v-if="modelValue && previewVisible" class="cover-preview">
      <img :src="imgSrc" alt="封面预览" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { uploadCover } from '@/api/upload'
import { ElMessage } from 'element-plus'

const props = defineProps<{ modelValue: string; module: string }>()
const emit = defineEmits<{ 'update:modelValue': [string] }>()

const previewVisible = ref(false)

const imgSrc = computed(() => {
  if (!props.modelValue) return ''
  if (props.modelValue.startsWith('http') || props.modelValue.startsWith('/')) return props.modelValue
  return `/${props.modelValue}`
})

const beforeUpload = (file: File) => {
  if (!file.type.startsWith('image/')) { ElMessage.error('请选择图片文件'); return false }
  if (file.size > 10 * 1024 * 1024) { ElMessage.error('图片大小不能超过10MB'); return false }
  return true
}

const handleRequest = async (options: any) => {
  try {
    const res: any = await uploadCover(options.file, props.module, `temp_${Date.now()}`)
    emit('update:modelValue', res.url)
    ElMessage.success('封面上传成功')
  } catch (e: any) {
    ElMessage.error(e?.message || '上传失败')
  }
}
</script>

<style scoped>
.cover-upload { display: flex; flex-direction: column; gap: 8px; }
.cover-actions { display: flex; gap: 8px; }
.cover-preview img { width: 100%; max-height: 200px; object-fit: cover; border-radius: 4px; border: 1px solid var(--el-border-color); margin-top: 4px; }
</style>
