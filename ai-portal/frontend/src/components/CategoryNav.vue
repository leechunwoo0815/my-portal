<template>
  <div class="category-nav">
    <el-menu
      :default-active="activeCategory"
      mode="horizontal"
      @select="handleSelect"
      :ellipsis="false"
    >
      <el-menu-item index="">全部</el-menu-item>
      <el-menu-item
        v-for="cat in categories"
        :key="cat.id"
        :index="cat.slug"
      >
        {{ cat.name }}
      </el-menu-item>
    </el-menu>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  categories: any[]
  activeCategory?: string
}>()

const emit = defineEmits<{
  select: [slug: string]
}>()

const handleSelect = (slug: string) => emit('select', slug)
</script>

<style scoped>
.category-nav .el-menu {
  border-bottom: none;
}
.category-nav .el-menu-item {
  font-size: 14px;
}
</style>
