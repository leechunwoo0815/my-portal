<template>
  <div class="tag-list">
    <el-tag
      v-for="tag in tags"
      :key="tag.id || tag"
      :type="activeTag === (tag.slug || tag) ? 'primary' : 'info'"
      :effect="activeTag === (tag.slug || tag) ? 'dark' : 'plain'"
      class="tag-item"
      @click="handleClick(tag)"
    >
      {{ tag.name || tag }}
    </el-tag>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  tags: any[]
  activeTag?: string
}>()

const emit = defineEmits<{
  select: [tag: any]
}>()

const handleClick = (tag: any) => emit('select', tag)
</script>

<style scoped>
.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.tag-item {
  cursor: pointer;
  transition: all 0.2s;
}
.tag-item:hover {
  opacity: 0.8;
}
</style>
