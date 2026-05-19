<template>
  <el-button
    ref="btnRef"
    :type="favorited ? 'warning' : 'default'"
    size="small"
    :loading="loading"
    class="fav-btn"
    @click.stop.prevent="handleToggle"
  >
    <el-icon><CollectionTag /></el-icon>
    {{ count > 0 ? count : '' }}
  </el-button>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { toggleFavorite, checkFavorited } from '@/api/interaction'
import { ElMessage } from 'element-plus'
import { CollectionTag } from '@element-plus/icons-vue'

const props = defineProps<{
  targetType: string
  targetId: number
  count?: number
}>()

const emit = defineEmits<{
  change: [favorited: boolean, count: number]
}>()

const favorited = ref(false)
const count = ref(props.count || 0)
const loading = ref(false)
const btnRef = ref()

const triggerBounce = () => {
  const el = btnRef.value?.$el || btnRef.value
  if (el) {
    el.classList.remove('fav-animate')
    void el.offsetWidth
    el.classList.add('fav-animate')
    setTimeout(() => el.classList.remove('fav-animate'), 350)
  }
}

onMounted(async () => {
  try {
    const res: any = await checkFavorited(props.targetType, props.targetId)
    favorited.value = !!res?.favorited
  } catch {}
})

const handleToggle = async () => {
  loading.value = true
  try {
    const res: any = await toggleFavorite({ target_type: props.targetType, target_id: props.targetId })
    favorited.value = res?.favorited ?? !favorited.value
    count.value = res?.count ?? count.value + (favorited.value ? 1 : -1)
    emit('change', favorited.value, count.value)
    if (favorited.value) triggerBounce()
  } catch (e) {
    ElMessage.error('操作失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.fav-btn {
  transition: transform 0.15s ease, background-color 0.2s ease, border-color 0.2s ease;
}
.fav-btn:hover {
  transform: scale(1.05);
}
.fav-btn:active {
  transform: scale(0.95);
}
:deep(.fav-animate) {
  animation: fav-bounce 0.35s ease;
}
@keyframes fav-bounce {
  0% { transform: scale(1); }
  30% { transform: scale(1.25); }
  60% { transform: scale(0.95); }
  100% { transform: scale(1); }
}
</style>
