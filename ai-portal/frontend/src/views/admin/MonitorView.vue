<template>
  <div class="monitor-view">
    <!-- 实时监控卡片 -->
    <div class="monitor-cards">
      <el-card v-for="metric in metrics" :key="metric.label" class="metric-card" shadow="hover">
        <div class="metric-header">
          <el-icon :size="28"><component :is="metric.icon" /></el-icon>
          <span class="metric-label">{{ metric.label }}</span>
        </div>
        <div class="metric-value" :class="metric.status">
          {{ metric.value }}
          <span class="metric-unit">{{ metric.unit }}</span>
        </div>
        <el-progress
          :percentage="metric.percent"
          :color="metric.color"
          :stroke-width="8"
          :show-text="false"
        />
      </el-card>
    </div>

    <!-- 进程信息 -->
    <el-card shadow="hover" class="process-card">
      <template #header>
        <span>后端服务进程</span>
        <el-tag :type="processInfo?.memory_mb > 700 ? 'danger' : 'success'" size="small">
          {{ processInfo?.memory_mb > 700 ? '内存超标' : '运行正常' }}
        </el-tag>
      </template>
      <el-descriptions :column="3" border>
        <el-descriptions-item label="PID">{{ processInfo?.pid }}</el-descriptions-item>
        <el-descriptions-item label="进程名">{{ processInfo?.name }}</el-descriptions-item>
        <el-descriptions-item label="状态">{{ processInfo?.status }}</el-descriptions-item>
        <el-descriptions-item label="内存占用">
          <span :class="{ 'text-danger': processInfo?.memory_mb > 700 }">
            {{ processInfo?.memory_mb }} MB
          </span>
        </el-descriptions-item>
        <el-descriptions-item label="内存占比">{{ processInfo?.memory_percent }}%</el-descriptions-item>
        <el-descriptions-item label="线程数">{{ processInfo?.threads }}</el-descriptions-item>
      </el-descriptions>
      <div v-if="processInfo?.memory_mb > 700" class="memory-warning">
        <el-alert
          title="内存占用超过700MB红线！"
          type="error"
          description="建议检查是否有内存泄漏，或重启后端服务。"
          show-icon
          :closable="false"
        />
      </div>
    </el-card>

    <!-- 系统信息 -->
    <el-card shadow="hover">
      <template #header>
        <span>系统信息</span>
      </template>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="CPU核心数">{{ systemInfo?.cpu_logical_cores }} 逻辑 / {{ systemInfo?.cpu_physical_cores }} 物理</el-descriptions-item>
        <el-descriptions-item label="内存总量">{{ systemInfo?.memory_total_gb }} GB</el-descriptions-item>
        <el-descriptions-item label="磁盘总量">{{ systemInfo?.disk_total_gb }} GB</el-descriptions-item>
        <el-descriptions-item label="启动时间">{{ systemInfo?.boot_time }}</el-descriptions-item>
      </el-descriptions>
    </el-card>
  </div>
</template>

<script setup lang="ts">
/**
 * 系统监控页面
 * 实时展示CPU、内存、磁盘使用率，后端进程内存监控
 */
import { ref, onMounted, onUnmounted } from 'vue'
import { getMonitor, getSystemInfo, getProcessInfo } from '@/api/admin'
import { Cpu, Monitor, Folder, Warning } from '@element-plus/icons-vue'

const metrics = ref([
  { label: 'CPU使用率', value: 0, unit: '%', percent: 0, icon: Cpu, color: '#409eff', status: '' },
  { label: '内存使用率', value: 0, unit: '%', percent: 0, icon: Monitor, color: '#67c23a', status: '' },
  { label: '磁盘使用率', value: 0, unit: '%', percent: 0, icon: Folder, color: '#e6a23c', status: '' },
])

const processInfo = ref<any>(null)
const systemInfo = ref<any>(null)
let timer: ReturnType<typeof setInterval>

const fetchData = async () => {
  try {
    // 系统监控
    const monitorRes: any = await getMonitor()
    const data = monitorRes.data
    metrics.value = [
      {
        ...metrics.value[0],
        value: data.cpu_percent,
        percent: Math.min(data.cpu_percent, 100),
        status: data.cpu_percent > 80 ? 'danger' : data.cpu_percent > 60 ? 'warning' : '',
      },
      {
        ...metrics.value[1],
        value: data.memory_percent,
        percent: Math.min(data.memory_percent, 100),
        status: data.memory_percent > 80 ? 'danger' : data.memory_percent > 60 ? 'warning' : '',
      },
      {
        ...metrics.value[2],
        value: data.disk_percent,
        percent: Math.min(data.disk_percent, 100),
        status: data.disk_percent > 80 ? 'danger' : data.disk_percent > 60 ? 'warning' : '',
      },
    ]

    // 进程信息
    const procRes: any = await getProcessInfo()
    processInfo.value = procRes.data

    // 系统信息（只加载一次）
    if (!systemInfo.value) {
      const sysRes: any = await getSystemInfo()
      systemInfo.value = sysRes.data
    }
  } catch (error) {
    // 静默处理
  }
}

onMounted(() => {
  fetchData()
  // 每5秒刷新一次
  timer = setInterval(fetchData, 5000)
})

onUnmounted(() => {
  clearInterval(timer)
})
</script>

<style scoped lang="scss">
.monitor-view {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.monitor-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
}

.metric-card {
  background-color: var(--app-bg-card);
  border: 1px solid var(--app-border);

  .metric-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 12px;
    color: var(--app-text-secondary);

    .metric-label {
      font-size: 14px;
    }
  }

  .metric-value {
    font-size: 36px;
    font-weight: 700;
    color: var(--app-text);
    margin-bottom: 12px;

    .metric-unit {
      font-size: 16px;
      font-weight: 400;
      color: var(--app-text-secondary);
    }

    &.warning {
      color: var(--el-color-warning);
    }

    &.danger {
      color: var(--el-color-danger);
    }
  }
}

.process-card {
  background-color: var(--app-bg-card);
  border: 1px solid var(--app-border);

  .memory-warning {
    margin-top: 16px;
  }
}
</style>
