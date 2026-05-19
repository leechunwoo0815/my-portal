<template>
  <div class="dashboard-view">
    <div class="stats-grid">
      <div v-for="stat in stats" :key="stat.label" class="stat-card">
        <div class="stat-value font-mono">{{ stat.value }}</div>
        <div class="stat-label">{{ stat.label }}</div>
        <div class="stat-icon">{{ stat.icon }}</div>
        <div class="stat-glow" />
      </div>
    </div>

    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-card-header font-mono">
          <span class="prefix">>_</span> 近7天API调用趋势
        </div>
        <div ref="chartRef" class="chart-container" />
      </div>

      <div class="chart-card">
        <div class="chart-card-header font-mono">
          <span class="prefix">>_</span> 模型使用分布
        </div>
        <div ref="pieRef" class="chart-container" />
      </div>
    </div>

    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-card-header font-mono">
          <span class="prefix">>_</span> 内容发布统计
        </div>
        <div ref="barRef" class="chart-container" />
      </div>

      <div class="chart-card">
        <div class="chart-card-header font-mono">
          <span class="prefix">>_</span> 用户活跃度
        </div>
        <div ref="radarRef" class="chart-container" />
      </div>
    </div>

    <div class="quick-actions-card">
      <div class="chart-card-header font-mono">
        <span class="prefix">>_</span> 快捷操作
      </div>
      <div class="quick-actions">
        <el-button type="primary" @click="$router.push('/admin/projects')">
          <el-icon><Plus /></el-icon>新建项目
        </el-button>
        <el-button type="success" @click="$router.push('/admin/blogs')">
          <el-icon><Plus /></el-icon>新建博客
        </el-button>
        <el-button type="warning" @click="$router.push('/admin/api-keys')">
          <el-icon><Key /></el-icon>配置API密钥
        </el-button>
        <el-button type="info" @click="$router.push('/admin/knowledge')">
          <el-icon><Upload /></el-icon>上传知识库
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { getDashboardStats as getStats } from '@/api/admin'
import * as echarts from 'echarts'
import { Plus, Key, Upload } from '@element-plus/icons-vue'

const stats = ref([
  { label: '总会话数', value: 0, icon: '💬' },
  { label: '总消息数', value: 0, icon: '📨' },
  { label: '总项目数', value: 0, icon: '📁' },
  { label: '总博客数', value: 0, icon: '📝' },
  { label: '今日调用', value: 0, icon: '⚡' },
  { label: '今日Token', value: 0, icon: '🔢' },
  { label: '总用户数', value: 0, icon: '👥' },
])

const chartRef = ref<HTMLElement>()
const pieRef = ref<HTMLElement>()
const barRef = ref<HTMLElement>()
const radarRef = ref<HTMLElement>()
let lineChart: echarts.ECharts | null = null
let pieChart: echarts.ECharts | null = null
let barChart: echarts.ECharts | null = null
let radarChart: echarts.ECharts | null = null

const getCssVar = (name: string) => getComputedStyle(document.documentElement).getPropertyValue(name).trim()

const CYBER_COLORS = ['#00d4aa', '#f0b429', '#626aef', '#ff6b6b', '#4ecdc4', '#a855f7', '#06b6d4']
const NEON_GREEN = '#00d4aa'
const AMBER_GOLD = '#f0b429'

onMounted(async () => {
  try {
    const data: any = await getStats()
    stats.value[0].value = data.total_conversations
    stats.value[1].value = data.total_messages
    stats.value[2].value = data.total_projects
    stats.value[3].value = data.total_blogs
    stats.value[4].value = data.today_api_calls
    stats.value[5].value = data.today_token_usage
    stats.value[6].value = data.total_users
  } catch (error) { console.error(error) }

  const textColor = getCssVar('--cyber-muted') || getCssVar('--el-text-color-secondary') || '#8daac5'
  const lineColor = getCssVar('--cyber-border') || getCssVar('--el-border-color') || '#5a7a96'
  const cardBg = getCssVar('--cyber-card') || getCssVar('--app-bg-card') || '#0a1929'

  if (chartRef.value) {
    lineChart = echarts.init(chartRef.value)
    lineChart.setOption({
      backgroundColor: 'transparent',
      grid: { top: 30, right: 20, bottom: 30, left: 50 },
      xAxis: {
        type: 'category',
        data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
        axisLine: { lineStyle: { color: lineColor } },
        axisLabel: { color: textColor },
      },
      yAxis: {
        type: 'value',
        axisLine: { lineStyle: { color: lineColor } },
        axisLabel: { color: textColor },
        splitLine: { lineStyle: { color: lineColor, type: 'dashed' } },
      },
      series: [{
        data: [12, 19, 8, 25, 15, 30, 22],
        type: 'line',
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(0, 212, 170, 0.3)' },
            { offset: 1, color: 'rgba(0, 212, 170, 0.02)' },
          ]),
        },
        lineStyle: { color: NEON_GREEN, width: 2 },
        itemStyle: { color: NEON_GREEN, borderColor: '#fff', borderWidth: 1 },
      }],
    })
  }

  if (pieRef.value) {
    pieChart = echarts.init(pieRef.value)
    pieChart.setOption({
      backgroundColor: 'transparent',
      series: [{
        type: 'pie',
        radius: ['40%', '70%'],
        data: [
          { value: 35, name: 'DeepSeek', itemStyle: { color: NEON_GREEN } },
          { value: 25, name: '智谱GLM', itemStyle: { color: AMBER_GOLD } },
          { value: 20, name: '通义千问', itemStyle: { color: '#626aef' } },
          { value: 20, name: '豆包', itemStyle: { color: '#06b6d4' } },
        ],
        label: { color: textColor, fontSize: 12 },
        itemStyle: {
          borderRadius: 6,
          borderColor: cardBg,
          borderWidth: 2,
        },
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowColor: 'rgba(0, 212, 170, 0.5)',
          },
        },
      }],
    })
  }

  if (barRef.value) {
    barChart = echarts.init(barRef.value)
    barChart.setOption({
      backgroundColor: 'transparent',
      grid: { top: 30, right: 20, bottom: 30, left: 50 },
      xAxis: {
        type: 'category',
        data: ['博客', '新闻', '产品', '方案', '项目'],
        axisLine: { lineStyle: { color: lineColor } },
        axisLabel: { color: textColor },
      },
      yAxis: {
        type: 'value',
        axisLine: { lineStyle: { color: lineColor } },
        axisLabel: { color: textColor },
        splitLine: { lineStyle: { color: lineColor, type: 'dashed' } },
      },
      series: [{
        data: [
          { value: 42, itemStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: NEON_GREEN }, { offset: 1, color: 'rgba(0,212,170,0.3)' }]) } },
          { value: 28, itemStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: AMBER_GOLD }, { offset: 1, color: 'rgba(240,180,41,0.3)' }]) } },
          { value: 15, itemStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: '#626aef' }, { offset: 1, color: 'rgba(98,106,239,0.3)' }]) } },
          { value: 10, itemStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: '#06b6d4' }, { offset: 1, color: 'rgba(6,182,212,0.3)' }]) } },
          { value: 8, itemStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: '#a855f7' }, { offset: 1, color: 'rgba(168,85,247,0.3)' }]) } },
        ],
        type: 'bar',
        barWidth: '50%',
        borderRadius: [4, 4, 0, 0],
      }],
    })
  }

  if (radarRef.value) {
    radarChart = echarts.init(radarRef.value)
    radarChart.setOption({
      backgroundColor: 'transparent',
      radar: {
        indicator: [
          { name: '博客', max: 100 },
          { name: '评论', max: 100 },
          { name: '点赞', max: 100 },
          { name: '收藏', max: 100 },
          { name: '签到', max: 100 },
          { name: '动态', max: 100 },
        ],
        axisName: { color: textColor, fontSize: 11 },
        splitLine: { lineStyle: { color: lineColor } },
        splitArea: { areaStyle: { color: ['transparent'] } },
        axisLine: { lineStyle: { color: lineColor } },
      },
      series: [{
        type: 'radar',
        data: [{
          value: [80, 60, 75, 45, 90, 55],
          name: '活跃度',
          areaStyle: { color: 'rgba(0, 212, 170, 0.15)' },
          lineStyle: { color: NEON_GREEN, width: 2 },
          itemStyle: { color: NEON_GREEN },
        }],
      }],
    })
  }

  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  lineChart?.dispose()
  pieChart?.dispose()
  barChart?.dispose()
  radarChart?.dispose()
})

const handleResize = () => {
  lineChart?.resize()
  pieChart?.resize()
  barChart?.resize()
  radarChart?.resize()
}
</script>

<style scoped lang="scss">
.dashboard-view {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;

  @media (max-width: 1024px) {
    grid-template-columns: repeat(2, 1fr);
  }
  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
}

.stat-card {
  position: relative;
  background: var(--cyber-card, var(--app-bg-card));
  border: 1px solid var(--cyber-border, var(--app-border));
  border-radius: 10px;
  padding: 20px;
  overflow: hidden;
  transition: border-color 0.2s, box-shadow 0.2s;

  &:hover {
    border-color: var(--cyber-neon, var(--app-accent));
    box-shadow: 0 0 12px rgba(0, 212, 170, 0.1);
  }

  .stat-value {
    font-size: 28px;
    font-weight: 700;
    color: var(--cyber-neon, var(--app-accent));
    margin-bottom: 4px;
  }

  .stat-label {
    font-size: 13px;
    color: var(--cyber-muted, var(--app-text-secondary));
  }

  .stat-icon {
    position: absolute;
    top: 14px;
    right: 14px;
    font-size: 28px;
    opacity: 0.2;
  }

  .stat-glow {
    position: absolute;
    bottom: -20px;
    right: -20px;
    width: 80px;
    height: 80px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(0, 212, 170, 0.08) 0%, transparent 70%);
    pointer-events: none;
  }
}

.charts-row {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 16px;

  @media (max-width: 1024px) {
    grid-template-columns: 1fr;
  }
}

.chart-card {
  background: var(--cyber-card, var(--app-bg-card));
  border: 1px solid var(--cyber-border, var(--app-border));
  border-radius: 10px;
  overflow: hidden;
}

.chart-card-header {
  padding: 14px 16px;
  border-bottom: 1px solid var(--cyber-border, var(--app-border));
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--cyber-text, var(--app-text));
}

.chart-card-header .prefix {
  color: var(--cyber-neon, var(--app-accent));
}

.chart-container {
  height: 280px;
}

.quick-actions-card {
  background: var(--cyber-card, var(--app-bg-card));
  border: 1px solid var(--cyber-border, var(--app-border));
  border-radius: 10px;
  overflow: hidden;
}

.quick-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  padding: 16px;
}
</style>
