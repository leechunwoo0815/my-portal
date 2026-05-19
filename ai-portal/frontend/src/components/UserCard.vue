<template>
  <div class="user-card" role="button" tabindex="0" :aria-label="user.nickname || user.username" @click="$emit('click', user)" @keydown.enter="$emit('click', user)">
    <el-avatar :size="48" :src="user.avatar_url">
      {{ (user.nickname || user.username || '?')[0] }}
    </el-avatar>
    <div class="user-card__info">
      <div class="user-card__name">{{ user.nickname || user.username }}</div>
      <div class="user-card__bio" v-if="user.bio">{{ user.bio }}</div>
      <div class="user-card__stats">
        <span>文章 {{ user.blog_count || 0 }}</span>
        <span>粉丝 {{ user.followers_count || 0 }}</span>
        <span>获赞 {{ user.like_count || 0 }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  user: any
}>()

defineEmits<{
  click: [user: any]
}>()
</script>

<style scoped>
.user-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  cursor: pointer;
  border-radius: 8px;
  transition: background 0.2s;
}
.user-card:hover {
  background: var(--el-fill-color-light);
}
.user-card__info {
  flex: 1;
  min-width: 0;
}
.user-card__name {
  font-weight: 600;
  font-size: 14px;
}
.user-card__bio {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-top: 2px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.user-card__stats {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: var(--el-text-color-placeholder);
  margin-top: 4px;
}
</style>
