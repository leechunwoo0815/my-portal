<template>
  <div class="contribution-graph">
    <div class="graph-header">
      <span class="graph-title">{{ totalDays }} 天内活跃 {{ activeDays }} 天</span>
    </div>
    <div class="graph-container">
      <div class="graph-months">
        <span v-for="m in monthLabels" :key="m.label" :style="{ gridColumn: m.col }">{{ m.label }}</span>
      </div>
      <div class="graph-grid">
        <div class="graph-days">
          <span>一</span><span>三</span><span>五</span>
        </div>
        <div class="graph-cells">
          <div
            v-for="(day, idx) in gridDays"
            :key="idx"
            :class="['graph-cell', `level-${day.level}`]"
            :title="day.date ? `${day.date}: ${day.count ? day.count + ' 次活动' : '无活动'}` : ''"
          />
        </div>
      </div>
    </div>
    <div class="graph-legend">
      <span>少</span>
      <div class="graph-cell level-0" />
      <div class="graph-cell level-1" />
      <div class="graph-cell level-2" />
      <div class="graph-cell level-3" />
      <div class="graph-cell level-4" />
      <span>多</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  dates: string[] // Array of date strings like "2024-01-15"
}>()

const totalDays = 364

const dateSet = computed(() => {
  const set = new Map<string, number>()
  for (const d of props.dates) {
    const key = d.slice(0, 10)
    set.set(key, (set.get(key) || 0) + 1)
  }
  return set
})

const activeDays = computed(() => dateSet.value.size)

const gridDays = computed(() => {
  const today = new Date()
  const days: { date: string; count: number; level: number }[] = []

  // Find the last Saturday (end of week)
  const end = new Date(today)
  end.setDate(end.getDate() + (6 - end.getDay()))

  // Go back 52 weeks
  const start = new Date(end)
  start.setDate(start.getDate() - totalDays)

  // Fill in days from start to end
  const current = new Date(start)
  while (current <= end) {
    const dateStr = current.toISOString().slice(0, 10)
    const count = dateSet.value.get(dateStr) || 0
    let level = 0
    if (count >= 5) level = 4
    else if (count >= 3) level = 3
    else if (count >= 2) level = 2
    else if (count >= 1) level = 1

    days.push({ date: dateStr, count, level })
    current.setDate(current.getDate() + 1)
  }

  // Pad to complete the first week
  while (days.length % 7 !== 0) {
    days.unshift({ date: '', count: 0, level: 0 })
  }

  return days
})

const monthLabels = computed(() => {
  const labels: { label: string; col: number }[] = []
  let lastMonth = -1
  const cols = Math.ceil(gridDays.value.length / 7)

  for (let col = 0; col < cols; col++) {
    const dayIdx = col * 7
    const day = gridDays.value[dayIdx]
    if (day?.date) {
      const month = new Date(day.date).getMonth()
      if (month !== lastMonth) {
        const monthNames = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']
        labels.push({ label: monthNames[month], col: col + 1 })
        lastMonth = month
      }
    }
  }
  return labels
})
</script>

<style scoped>
.contribution-graph {
  padding: 16px;
  background: var(--app-bg-card, #fff);
  border: 1px solid var(--app-border);
  border-radius: 12px;
}
.graph-header {
  margin-bottom: 12px;
}
.graph-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--app-text);
}
.graph-container {
  overflow-x: auto;
}
.graph-months {
  display: grid;
  grid-auto-flow: column;
  grid-auto-columns: 14px;
  gap: 2px;
  margin-bottom: 4px;
  padding-left: 28px;
}
.graph-months span {
  font-size: 10px;
  color: var(--app-text-secondary);
}
.graph-grid {
  display: flex;
  gap: 4px;
}
.graph-days {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding-top: 2px;
}
.graph-days span {
  font-size: 10px;
  color: var(--app-text-secondary);
  height: 12px;
  line-height: 12px;
}
.graph-cells {
  display: grid;
  grid-auto-flow: column;
  grid-template-rows: repeat(7, 12px);
  gap: 2px;
}
.graph-cell {
  width: 12px;
  height: 12px;
  border-radius: 2px;
  outline: 1px solid rgba(0, 0, 0, 0.06);
}
.level-0 { background: var(--app-bg, #ebedf0); }
.level-1 { background: #9be9a8; }
.level-2 { background: #40c463; }
.level-3 { background: #30a14e; }
.level-4 { background: #216e39; }

.graph-legend {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 8px;
  justify-content: flex-end;
  font-size: 10px;
  color: var(--app-text-secondary);
}
.graph-legend .graph-cell {
  width: 10px;
  height: 10px;
}

@media (prefers-color-scheme: dark) {
  .level-0 { background: #161b22; }
  .level-1 { background: #0e4429; }
  .level-2 { background: #006d32; }
  .level-3 { background: #26a641; }
  .level-4 { background: #39d353; }
}
</style>
