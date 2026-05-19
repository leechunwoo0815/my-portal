<template>
  <div class="not-found">
    <h1>404</h1>
    <p>页面不存在</p>
    <el-button type="primary" @click="$router.push('/')">返回首页</el-button>
  </div>
</template>

<style scoped>
.not-found { display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 60vh; }
.not-found h1 { font-size: 6rem; color: var(--el-color-primary); margin: 0; }
.not-found p { font-size: 1.2rem; color: var(--el-text-color-secondary); margin: 16px 0 24px; }
</style>
