<template>
  <!-- 根组件：根据路由配置自动渲染对应布局 -->
  <router-view />
</template>

<script setup lang="ts">
/**
 * App.vue - 应用根组件
 * 所有页面通过router-view渲染
 * 全局状态（如主题、语言）可在此初始化
 */
import { onMounted } from 'vue'

onMounted(() => {
  // 页面加载完成后移除loading动画（如果有）
  const loadingEl = document.getElementById('app-loading')
  if (loadingEl) {
    loadingEl.style.display = 'none'
  }
})
</script>


