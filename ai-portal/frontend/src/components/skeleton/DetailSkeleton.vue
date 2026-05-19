<template>
  <div class="detail-skeleton">
    <div class="skeleton-bone tag-bone" />
    <div class="skeleton-bone title-lg w-4-5" />
    <div class="skeleton-bone title-lg w-3-5" />
    <div class="skeleton-author-row">
      <div class="skeleton-avatar" />
      <div class="skeleton-bone w-24" />
      <div class="skeleton-bone tag-bone-sm" />
    </div>
    <div class="skeleton-meta-row">
      <div class="skeleton-bone w-24" />
      <div class="skeleton-bone w-20" />
    </div>
    <div class="skeleton-tags-row">
      <div class="skeleton-bone tag-bone" />
      <div class="skeleton-bone tag-bone" />
      <div class="skeleton-bone tag-bone sm" />
    </div>
    <div class="skeleton-cover" />
    <div class="skeleton-content">
      <div class="skeleton-bone w-full" />
      <div class="skeleton-bone w-full" />
      <div class="skeleton-bone w-5-6" />
      <div class="skeleton-bone w-full" />
      <div class="skeleton-bone w-4-5" />
      <div class="skeleton-bone w-full" />
      <div class="skeleton-bone w-3-4" />
      <div class="skeleton-bone w-full" />
      <div class="skeleton-bone w-5-6" />
      <div class="skeleton-bone w-2-3" />
    </div>
  </div>
</template>

<script setup lang="ts">
</script>

<style scoped>
.detail-skeleton {
  max-width: 800px;
  margin: 0 auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 14px;
  animation: skeleton-pulse 1.5s ease-in-out infinite;
}
.skeleton-bone {
  height: 14px;
  border-radius: 4px;
  background: var(--cyber-border, var(--app-border));
}
.title-lg {
  height: 28px;
}
.tag-bone {
  width: 60px;
  height: 22px;
}
.tag-bone-sm {
  width: 48px;
  height: 18px;
}
.skeleton-author-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 4px;
}
.skeleton-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--cyber-border, var(--app-border));
  flex-shrink: 0;
}
.skeleton-meta-row {
  display: flex;
  gap: 16px;
}
.skeleton-meta-row .skeleton-bone {
  height: 12px;
}
.skeleton-tags-row {
  display: flex;
  gap: 8px;
}
.skeleton-cover {
  width: 100%;
  height: 300px;
  border-radius: 8px;
  background: var(--cyber-border, var(--app-border));
}
.skeleton-content {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 8px;
}

.w-full { width: 100%; }
.w-5-6 { width: 83%; }
.w-4-5 { width: 80%; }
.w-3-4 { width: 75%; }
.w-3-5 { width: 60%; }
.w-2-3 { width: 67%; }
.w-24 { width: 96px; }
.w-20 { width: 80px; }

@keyframes skeleton-pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
</style>
