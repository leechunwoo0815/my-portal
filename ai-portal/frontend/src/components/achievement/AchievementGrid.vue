<template>
  <div class="achievement-grid">
    <div class="grid-header">
      <h3 class="font-mono text-cyber-neon">[成就系统]</h3>
      <div class="stats">
        <span class="stat-item">已解锁 <strong class="text-cyber-neon">{{ unlockedCount }}</strong>/{{ total }}</span>
        <span class="stat-item">积分 <strong class="text-cyber-amber">{{ totalPoints }}</strong></span>
      </div>
    </div>

    <div class="grid-container">
      <div
        v-for="item in achievements"
        :key="item.code"
        class="achievement-card"
        :class="[`tier-${item.tier}`, { 'locked': !item.is_unlocked, 'secret': item.is_secret && !item.is_unlocked }]"
      >
        <div class="ach-icon">{{ item.icon }}</div>
        <div class="ach-info">
          <div class="ach-name">{{ item.name }}</div>
          <div class="ach-desc">{{ item.description }}</div>
          <div v-if="!item.is_unlocked && !item.is_secret" class="ach-progress">
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: progressPercent(item) + '%' }" />
            </div>
            <span class="progress-text font-mono">{{ item.progress }}/{{ item.condition_value }}</span>
          </div>
        </div>
        <div v-if="item.is_unlocked" class="ach-check">✓</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { achievementApi } from '@/api/achievement'

interface AchievementItem {
  code: string
  name: string
  description: string
  icon: string
  tier: string
  points: number
  is_unlocked: boolean
  is_secret: boolean
  progress: number
  condition_value: number
}

const achievements = ref<AchievementItem[]>([])
const unlockedCount = ref(0)
const totalPoints = ref(0)
const total = computed(() => achievements.value.length)

const loadAchievements = async () => {
  try {
    const res: any = await achievementApi.list()
    achievements.value = res.items || []
    unlockedCount.value = res.unlocked_count || 0
    totalPoints.value = res.total_points || 0
  } catch {}
}

const progressPercent = (item: AchievementItem) => {
  if (item.condition_value <= 0) return 0
  return Math.min(Math.round((item.progress / item.condition_value) * 100), 100)
}

onMounted(loadAchievements)
</script>

<style scoped>
.achievement-grid {
  padding: 16px;
}

.grid-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.stats {
  display: flex;
  gap: 16px;
  font-size: 14px;
  color: var(--cyber-muted);
}

.grid-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 12px;
}

.achievement-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 8px;
  background: var(--cyber-card);
  border: 1px solid var(--cyber-border);
  transition: all 0.25s;
  position: relative;
}

.achievement-card:hover {
  border-color: var(--cyber-neon);
  box-shadow: 0 0 10px rgba(0, 212, 170, 0.15);
}

.achievement-card.locked {
  opacity: 0.6;
}

.achievement-card.tier-bronze.is_unlocked { border-left: 3px solid #cd7f32; }
.achievement-card.tier-silver.is_unlocked { border-left: 3px solid #c0c0c0; }
.achievement-card.tier-gold.is_unlocked { border-left: 3px solid #ffd700; }
.achievement-card.tier-diamond.is_unlocked { border-left: 3px solid #b9f2ff; box-shadow: 0 0 15px rgba(185, 242, 255, 0.2); }

.ach-icon {
  font-size: 28px;
  flex-shrink: 0;
}

.ach-info {
  flex: 1;
  min-width: 0;
}

.ach-name {
  font-family: 'JetBrains Mono', monospace;
  font-size: 14px;
  font-weight: 600;
  color: var(--cyber-text);
}

.ach-desc {
  font-size: 12px;
  color: var(--cyber-muted);
  margin-top: 2px;
}

.ach-progress {
  margin-top: 6px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.progress-bar {
  flex: 1;
  height: 4px;
  background: var(--cyber-border);
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--cyber-neon);
  border-radius: 2px;
  transition: width 0.3s;
}

.progress-text {
  font-size: 11px;
  color: var(--cyber-muted);
  white-space: nowrap;
}

.ach-check {
  color: var(--cyber-neon);
  font-size: 18px;
  font-weight: bold;
  flex-shrink: 0;
}
</style>
