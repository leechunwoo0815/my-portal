<template>
  <div :class="['skeleton-wrapper', `skeleton-${variant}`]">
    <div v-for="i in count" :key="i" class="skeleton-card" :class="{ 'skeleton-animate': animated }">
      <template v-if="variant === 'list'">
        <div class="skeleton-cover" />
        <div class="skeleton-content">
          <div class="skeleton-meta">
            <div class="skeleton-bone w-16" />
            <div class="skeleton-bone w-24" />
            <div class="skeleton-bone w-20" />
          </div>
          <div class="skeleton-bone title-line w-full" />
          <div class="skeleton-bone title-line w-3-4" />
          <div class="skeleton-bone w-full" />
          <div class="skeleton-bone w-5-6" />
          <div class="skeleton-footer">
            <div class="skeleton-tags">
              <div class="skeleton-bone tag-bone" />
              <div class="skeleton-bone tag-bone" />
              <div class="skeleton-bone tag-bone sm" />
            </div>
            <div class="skeleton-stats">
              <div class="skeleton-bone stat-bone" />
              <div class="skeleton-bone stat-bone" />
              <div class="skeleton-bone stat-bone" />
            </div>
          </div>
        </div>
      </template>
      <template v-else>
        <div class="skeleton-grid-meta">
          <div class="skeleton-bone tag-bone" />
          <div class="skeleton-bone stat-bone" />
        </div>
        <div class="skeleton-bone title-line w-full" />
        <div class="skeleton-bone title-line w-3-4" />
        <div class="skeleton-bone w-full" />
        <div class="skeleton-bone w-5-6" />
        <div class="skeleton-grid-footer">
          <div class="skeleton-bone w-16" />
          <div class="skeleton-bone stat-bone" />
          <div class="skeleton-bone stat-bone" />
          <div class="skeleton-bone w-24" />
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  count?: number
  variant?: 'list' | 'grid'
  animated?: boolean
}>(), {
  count: 4,
  variant: 'list',
  animated: true
})
</script>

<style scoped>
.skeleton-wrapper {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.skeleton-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}
.skeleton-grid .skeleton-card {
  flex-direction: column;
}

.skeleton-card {
  display: flex;
  background: var(--cyber-card, var(--app-bg-card));
  border: 1px solid var(--cyber-border, var(--app-border));
  border-radius: 8px;
  overflow: hidden;
}
.skeleton-animate .skeleton-bone,
.skeleton-animate .skeleton-cover {
  animation: skeleton-pulse 1.5s ease-in-out infinite;
}

.skeleton-cover {
  width: 200px;
  min-height: 150px;
  flex-shrink: 0;
  background: var(--cyber-border, var(--app-border));
}
.skeleton-content {
  flex: 1;
  padding: 16px 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.skeleton-bone {
  height: 14px;
  border-radius: 4px;
  background: var(--cyber-border, var(--app-border));
}
.title-line {
  height: 18px;
}
.skeleton-meta {
  display: flex;
  gap: 10px;
  align-items: center;
}
.skeleton-meta .skeleton-bone {
  height: 20px;
}
.skeleton-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: auto;
}
.skeleton-tags {
  display: flex;
  gap: 6px;
}
.tag-bone {
  width: 52px;
  height: 22px;
}
.tag-bone.sm {
  width: 36px;
}
.skeleton-stats {
  display: flex;
  gap: 12px;
}
.stat-bone {
  width: 36px;
  height: 14px;
}

.skeleton-grid-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.skeleton-grid-footer {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 8px;
}
.skeleton-grid-footer .skeleton-bone {
  height: 12px;
}

.w-full { width: 100%; }
.w-5-6 { width: 83%; }
.w-3-4 { width: 75%; }
.w-24 { width: 96px; }
.w-20 { width: 80px; }
.w-16 { width: 64px; }

@keyframes skeleton-pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

@media (max-width: 768px) {
  .skeleton-cover {
    width: 100%;
    min-height: 180px;
  }
  .skeleton-card {
    flex-direction: column;
  }
  .skeleton-grid {
    grid-template-columns: 1fr;
  }
}
</style>
