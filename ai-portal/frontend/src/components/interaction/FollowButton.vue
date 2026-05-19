<template>
  <el-button
    ref="btnRef"
    :type="isFollowing ? 'default' : 'primary'"
    size="small"
    :loading="loading"
    class="follow-btn"
    @click.stop.prevent="handleToggle"
  >
    {{ isFollowing ? '已关注' : '+ 关注' }}
  </el-button>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '@/api/client'
import { ElMessage } from 'element-plus'

const props = defineProps<{ userId: number }>()
const emit = defineEmits<{ change: [following: boolean] }>()

const isFollowing = ref(false)
const loading = ref(false)
const btnRef = ref()

const triggerBounce = () => {
  const el = btnRef.value?.$el || btnRef.value
  if (el) {
    el.classList.remove('follow-animate')
    void el.offsetWidth
    el.classList.add('follow-animate')
    setTimeout(() => el.classList.remove('follow-animate'), 300)
  }
}

onMounted(async () => {
  try {
    const res: any = await api.get(`/v1/user/follow/check?user_id=${props.userId}`)
    isFollowing.value = !!res?.is_following
  } catch {}
})

const handleToggle = async () => {
  loading.value = true
  try {
    const res: any = await api.post('/v1/user/follow', { user_id: props.userId })
    isFollowing.value = res?.is_following ?? !isFollowing.value
    emit('change', isFollowing.value)
    triggerBounce()
  } catch {
    ElMessage.error('操作失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.follow-btn {
  transition: transform 0.15s ease, all 0.2s ease;
  min-width: 80px;
}
.follow-btn:hover {
  transform: scale(1.05);
}
.follow-btn:active {
  transform: scale(0.95);
}
:deep(.follow-animate) {
  animation: follow-bounce 0.3s ease;
}
@keyframes follow-bounce {
  0% { transform: scale(1); }
  30% { transform: scale(1.15); }
  60% { transform: scale(0.95); }
  100% { transform: scale(1); }
}
</style>
