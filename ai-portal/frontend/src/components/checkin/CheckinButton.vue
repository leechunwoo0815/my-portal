<template>
  <div class="checkin-btn">
    <el-button
      :type="isCheckedIn ? 'info' : 'primary'"
      :loading="loading"
      @click="handleCheckin"
      round
      class="checkin-button"
      :class="{ 'checked': isCheckedIn }"
    >
      <template v-if="isCheckedIn">
        <el-icon><Check /></el-icon>
        已签到 · 连续{{ continuousDays }}天
      </template>
      <template v-else>
        <el-icon><Calendar /></el-icon>
        签到
      </template>
    </el-button>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Check, Calendar } from '@element-plus/icons-vue'
import { checkinApi } from '@/api/achievement'

const isCheckedIn = ref(false)
const continuousDays = ref(0)
const loading = ref(false)

const loadStatus = async () => {
  try {
    const res: any = await checkinApi.getStatus()
    isCheckedIn.value = res.is_checked_in
    continuousDays.value = res.continuous_days
  } catch {}
}

const handleCheckin = async () => {
  if (isCheckedIn.value || loading.value) return
  loading.value = true
  try {
    const res: any = await checkinApi.doCheckin()
    if (res.success) {
      isCheckedIn.value = true
      continuousDays.value = res.continuous_days
      ElMessage.success({
        message: `签到成功！+${res.points_awarded}积分${res.bonus_points > 0 ? ` (含奖励+${res.bonus_points})` : ''}`,
        duration: 3000,
      })
    } else {
      ElMessage.info(res.message)
      isCheckedIn.value = true
    }
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '签到失败')
  } finally {
    loading.value = false
  }
}

onMounted(loadStatus)
</script>

<style scoped>
.checkin-button {
  font-family: 'JetBrains Mono', monospace;
  font-size: 13px;
}
.checkin-button.checked {
  opacity: 0.7;
}
</style>
