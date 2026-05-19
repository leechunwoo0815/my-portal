<template>
  <div class="manage-view">
    <div class="page-header">
      <h2>{{ title }}</h2>
      <el-button type="primary" @click="$emit('create')">新建</el-button>
    </div>
    <slot name="filters" />
    <el-table :data="data" v-loading="loading" style="width:100%;margin-top:16px" stripe>
      <slot />
      <el-table-column label="操作" :width="actionWidth" fixed="right">
        <template #default="{ row }">
          <el-button size="small" link @click="$emit('edit', row)">编辑</el-button>
          <el-button size="small" link type="danger" @click="$emit('delete', row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <div style="text-align:right;margin-top:16px">
      <el-pagination v-if="total > 0" background layout="prev,pager,next,total" :total="total" :page-size="pageSize" v-model:current-page="currentPage" @current-change="$emit('page-change', $event)" />
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title: string
  data: any[]
  loading: boolean
  total: number
  pageSize: number
  currentPage: number
  actionWidth?: number
}>()

defineEmits(['create', 'edit', 'delete', 'page-change'])
</script>

<style scoped>
.manage-view { padding: 20px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; }
</style>
