<template>
  <div class="theme-toggle" role="button" tabindex="0" :aria-label="currentTheme === 'light' ? '切换到深色主题' : '切换到浅色主题'" @click="toggleTheme" @keydown.enter="toggleTheme">
    <el-button
      circle
      size="default"
      class="theme-button"
      :class="{ dark: isDark }"
      :title="currentTheme === 'light' ? '切换到深色主题' : '切换到浅色主题'"
      :aria-label="currentTheme === 'light' ? '切换到深色主题' : '切换到浅色主题'"
    >
      <el-icon class="theme-icon" :style="{ transform: isDark ? 'rotate(180deg)' : '' }">
        <component :is="themeIcon" />
      </el-icon>
    </el-button>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Sunny, Moon } from '@element-plus/icons-vue'
import { useThemeStore } from '@/stores/theme'

const themeStore = useThemeStore()

const currentTheme = computed(() => themeStore.currentTheme)
const isDark = computed(() => themeStore.isDark)
const themeIcon = computed(() => currentTheme.value === 'light' ? Moon : Sunny)

const toggleTheme = () => {
  themeStore.toggleTheme()
}
</script>

<style scoped>
.theme-toggle {
  display: inline-flex;
  align-items: center;
  cursor: pointer;
  margin: 0 8px;
}

.theme-button {
  border: 1px solid var(--el-border-color) !important;
  font-size: 18px;
  transition: all 0.3s ease;
}

.theme-button:hover {
  transform: scale(1.1);
  box-shadow: 0 2px 8px rgba(98, 106, 239, 0.3);
}

.theme-icon {
  font-size: 18px;
  transition: transform 0.4s ease;
}

.theme-button:hover .theme-icon {
  transform: rotate(360deg);
}
</style>
