<template>
  <div class="portfolio-view">
    <div class="portfolio-header">
      <h1>AI 作品集</h1>
      <p>展示 AI 在智慧城市、市政工程等领域的落地项目与应用案例</p>
    </div>

    <div v-if="loading" class="state-box">
      <el-skeleton :rows="5" animated />
    </div>
    <div v-else-if="error" class="state-box error">{{ error }}</div>
    <div v-else class="portfolio-grid">
      <el-card
        v-for="project in projects"
        :key="project.id"
        class="project-card"
        shadow="hover"
        @click="goToDetail(project.id)"
      >
        <div class="card-cover" v-if="project.cover_image">
          <img :src="project.cover_image" :alt="project.title" />
        </div>
        <div class="card-cover default-cover" v-else>
          <el-icon><Monitor /></el-icon>
        </div>
        <div class="card-body">
          <div class="card-meta">
            <el-tag size="small" type="primary">{{ project.category }}</el-tag>
            <span class="author-info" v-if="project.author_id">作者 ID: {{ project.author_id }}</span>
          </div>
          <h3 class="card-title">{{ project.title }}</h3>
          <p class="card-desc">{{ project.description }}</p>
          <div class="card-tags" v-if="project.tech_stack && project.tech_stack.length">
            <span v-for="tech in project.tech_stack" :key="tech" class="tech-tag">
              {{ tech }}
            </span>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getProjects } from '@/api/portfolio'
import { Monitor } from '@element-plus/icons-vue'

const router = useRouter()
const loading = ref(true)
const error = ref('')
const projects = ref<any[]>([])

const fetchProjects = async () => {
  loading.value = true
  try {
    const res: any = await getProjects({ page: 1, page_size: 50 })
    projects.value = res.items || res || []
  } catch (e: any) {
    error.value = e.message || '加载失败'
  } finally {
    loading.value = false
  }
}

const goToDetail = (id: number) => {
  router.push(`/portfolio/${id}`)
}

onMounted(() => {
  fetchProjects()
})
</script>

<style scoped>
.portfolio-view {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px;
  min-height: calc(100vh - 100px);
}

.portfolio-header {
  text-align: center;
  margin-bottom: 40px;
}
.portfolio-header h1 {
  font-size: 2.5rem;
  color: var(--el-text-color-primary);
  margin-bottom: 16px;
}
.portfolio-header p {
  font-size: 1.1rem;
  color: var(--el-text-color-secondary);
}

.state-box {
  padding: 60px 0;
  text-align: center;
}
.state-box.error {
  color: var(--el-color-danger);
}

.portfolio-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 24px;
}

.project-card {
  cursor: pointer;
  transition: transform 0.3s ease;
  display: flex;
  flex-direction: column;
  height: 100%;
}
.project-card:hover {
  transform: translateY(-5px);
}

.card-cover {
  height: 180px;
  background: var(--el-fill-color-light);
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}
.card-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.default-cover .el-icon {
  font-size: 64px;
  color: var(--el-text-color-placeholder);
}

.card-body {
  padding: 20px;
  display: flex;
  flex-direction: column;
  flex: 1;
}

.card-meta {
  margin-bottom: 12px;
}

.card-title {
  font-size: 1.25rem;
  color: var(--el-text-color-primary);
  margin: 0 0 12px 0;
  font-weight: 600;
  line-height: 1.4;
}

.card-desc {
  font-size: 0.95rem;
  color: var(--el-text-color-regular);
  line-height: 1.6;
  margin: 0 0 20px 0;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  flex: 1;
}

.card-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: auto;
}

.tech-tag {
  font-size: 0.75rem;
  color: var(--el-color-primary);
  background: var(--el-color-primary-light-9);
  padding: 2px 8px;
  border-radius: 4px;
}
</style>