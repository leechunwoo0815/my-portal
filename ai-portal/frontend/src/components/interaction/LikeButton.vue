<template>
  <el-button
    ref="btnRef"
    :type="liked ? 'primary' : 'default'"
    size="small"
    :loading="loading"
    class="like-btn"
    @click.stop.prevent="handleToggle"
  >
    <el-icon style="margin-right: 4px;">
      <StarFilled v-if="liked" />
      <Star v-else />
    </el-icon>
    {{ count > 0 ? count : '' }}
  </el-button>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Star, StarFilled } from '@element-plus/icons-vue'
import { toggleLike, checkLiked } from '@/api/interaction'
import { ElMessage } from 'element-plus'

const props = defineProps<{
  targetType: string
  targetId: number
  count?: number
}>()

const emit = defineEmits<{
  change: [liked: boolean, count: number]
}>()

const liked = ref(false)
const count = ref(props.count || 0)
const loading = ref(false)
const btnRef = ref()

const triggerBounce = () => {
  const el = btnRef.value?.$el || btnRef.value
  if (el) {
    el.classList.remove('like-animate')
    void el.offsetWidth
    el.classList.add('like-animate')
    setTimeout(() => el.classList.remove('like-animate'), 350)
  }
}

onMounted(async () => {
  try {
    const res: any = await checkLiked(props.targetType, props.targetId)
    liked.value = !!(res?.liked ?? res?.is_liked)
  } catch {}
})

const handleToggle = async () => {
  loading.value = true
  try {
    const res: any = await toggleLike({ target_type: props.targetType, target_id: props.targetId })
    liked.value = res?.liked ?? !liked.value
    count.value = res?.likes_count ?? count.value + (liked.value ? 1 : -1)
    emit('change', liked.value, count.value)
    if (liked.value) triggerBounce()
  } catch (e) {
    ElMessage.error('操作失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.like-btn {
  transition: transform 0.15s ease;
}
.like-btn:hover {
  transform: scale(1.05);
}
.like-btn:active {
  transform: scale(0.95);
}
:deep(.like-animate) {
  animation: like-bounce 0.35s ease;
}
@keyframes like-bounce {
  0% { transform: scale(1); }
  30% { transform: scale(1.25); }
  60% { transform: scale(0.95); }
  100% { transform: scale(1); }
}
</style>
