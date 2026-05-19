<template>
  <div class="search-skeleton-wrapper">
    <div v-for="i in count" :key="i" class="search-skeleton-item">
      <div class="skeleton-bone tag-bone" />
      <div class="search-skeleton-content">
        <div class="skeleton-bone title-line w-full" />
        <div class="skeleton-bone w-full" />
        <div class="skeleton-bone w-4-5" />
        <div class="search-skeleton-meta">
          <div class="skeleton-bone w-20" />
          <div class="skeleton-bone w-24" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  count?: number
}>(), {
  count: 5
})
</script>

<style scoped>
.search-skeleton-wrapper {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.search-skeleton-item {
  display: flex;
  gap: 12px;
  padding: 16px;
  border-bottom: 1px solid var(--cyber-border, var(--app-border));
  animation: skeleton-pulse 1.5s ease-in-out infinite;
}
.search-skeleton-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.skeleton-bone {
  height: 14px;
  border-radius: 4px;
  background: var(--cyber-border, var(--app-border));
}
.title-line {
  height: 18px;
}
.tag-bone {
  width: 50px;
  height: 22px;
  flex-shrink: 0;
}
.search-skeleton-meta {
  display: flex;
  gap: 12px;
}
.search-skeleton-meta .skeleton-bone {
  height: 12px;
}
.w-full { width: 100%; }
.w-4-5 { width: 80%; }
.w-24 { width: 96px; }
.w-20 { width: 80px; }

@keyframes skeleton-pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
</style>
