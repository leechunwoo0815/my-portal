<template>
  <el-card class="content-card" shadow="hover" @click="handleClick">
    <div class="content-card__header" v-if="item.cover_image">
      <img :src="item.cover_image" :alt="item.title" class="content-card__cover" />
    </div>
    <div class="content-card__body">
      <h3 class="content-card__title">{{ item.title }}</h3>
      <p class="content-card__summary" v-if="item.summary">{{ item.summary }}</p>
      <div class="content-card__meta">
        <span class="content-card__author" v-if="item.author">
          {{ item.author.nickname || item.author.username }}
        </span>
        <span class="content-card__date">{{ formatDate(item.created_at) }}</span>
        <span class="content-card__views" v-if="item.view_count">
          <el-icon><View /></el-icon> {{ item.view_count }}
        </span>
        <span class="content-card__likes" v-if="item.likes_count">
          <el-icon><Star /></el-icon> {{ item.likes_count }}
        </span>
      </div>
      <div class="content-card__tags" v-if="item.tags">
        <el-tag v-for="tag in parseTags(item.tags)" :key="tag" size="small" type="info">{{ tag }}</el-tag>
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { View, Star } from '@element-plus/icons-vue'

const props = defineProps<{
  item: any
  targetType?: string
}>()

const emit = defineEmits<{
  click: [item: any]
}>()

const handleClick = () => emit('click', props.item)

const formatDate = (v: string) => {
  if (!v) return ''
  const d = new Date(v)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

const parseTags = (tags: string) => {
  if (!tags) return []
  return tags.split(',').filter(Boolean).map((t: string) => t.trim())
}
</script>

<style scoped>
.content-card {
  cursor: pointer;
  transition: transform 0.2s;
  margin-bottom: 16px;
}
.content-card:hover {
  transform: translateY(-2px);
}
.content-card__cover {
  width: 100%;
  height: 180px;
  object-fit: cover;
  border-radius: 4px;
  margin-bottom: 12px;
}
.content-card__title {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 8px;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.content-card__summary {
  font-size: 13px;
  color: var(--el-text-color-secondary);
  margin: 0 0 8px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.content-card__meta {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 12px;
  color: var(--el-text-color-placeholder);
}
.content-card__meta .el-icon {
  margin-right: 2px;
}
.content-card__tags {
  margin-top: 8px;
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}
</style>
