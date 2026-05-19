<template>
  <div class="moment-skeleton-wrapper">
    <div v-for="i in count" :key="i" class="moment-skeleton-card">
      <div class="moment-skeleton-header">
        <div class="skeleton-avatar" />
        <div class="skeleton-info">
          <div class="skeleton-bone w-24" />
          <div class="skeleton-bone w-16" />
        </div>
      </div>
      <div class="moment-skeleton-body">
        <div class="skeleton-bone w-full" />
        <div class="skeleton-bone w-full" />
        <div class="skeleton-bone w-3-5" />
      </div>
      <div class="moment-skeleton-actions">
        <div class="skeleton-bone action-bone" />
        <div class="skeleton-bone action-bone" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  count?: number
}>(), {
  count: 3
})
</script>

<style scoped>
.moment-skeleton-wrapper {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.moment-skeleton-card {
  background: var(--cyber-card, var(--app-bg-card));
  border: 1px solid var(--cyber-border, var(--app-border));
  border-radius: 12px;
  padding: 16px 20px;
  animation: skeleton-pulse 1.5s ease-in-out infinite;
}
.moment-skeleton-header {
  display: flex;
  gap: 10px;
  align-items: center;
  margin-bottom: 12px;
}
.skeleton-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--cyber-border, var(--app-border));
  flex-shrink: 0;
}
.skeleton-info {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.skeleton-bone {
  height: 14px;
  border-radius: 4px;
  background: var(--cyber-border, var(--app-border));
}
.w-full { width: 100%; }
.w-3-5 { width: 60%; }
.w-24 { width: 96px; }
.w-16 { width: 64px; }

.moment-skeleton-body {
  padding-left: 50px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 12px;
}
.moment-skeleton-actions {
  padding-left: 50px;
  display: flex;
  gap: 16px;
}
.action-bone {
  width: 56px;
  height: 28px;
  border-radius: 6px;
}

@keyframes skeleton-pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
</style>
