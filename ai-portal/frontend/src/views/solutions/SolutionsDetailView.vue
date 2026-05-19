<template>
  <div class="solutions-detail-view">
    <div class="reading-progress" :style="{ width: progress + '%' }" />
    <div class="container">
      <!-- 返回按钮 -->
      <div class="back-link">
        <el-button type="text" @click="goBack">
          <el-icon><ArrowLeft /></el-icon>
          返回解决方案列表
        </el-button>
      </div>

      <!-- 解决方案内容 -->
      <article v-if="solution" class="solution-article" v-loading="loading">
        <!-- 解决方案头部 -->
        <header class="article-header">
          <el-tag :type="getCategoryType(solution.category)">{{ solution.category }}</el-tag>
          <h1 class="article-title">{{ solution.title }}</h1>
          <div class="article-author" v-if="solution.author">
            <router-link :to="`/user/${solution.author.id}`" class="author-link" :aria-label="solution.author.nickname || solution.author.username">
              <el-avatar :size="36" :src="solution.author.avatar_url">{{ solution.author.nickname?.[0] || solution.author.username?.[0] }}</el-avatar>
            </router-link>
            <div class="author-info">
              <router-link :to="`/user/${solution.author.id}`" class="author-link">
                <span class="author-name">{{ solution.author.nickname || solution.author.username }}</span>
              </router-link>
              <el-tag size="small" :type="solution.author.level === 999 ? 'success' : 'warning'">
                {{ solution.author.level === 999 ? '管理员' : 'LV' + solution.author.level }}
              </el-tag>
            </div>
          </div>
          <div class="article-meta">
            <span>{{ formatDate(solution.created_at) }}</span>
            <span class="solution-status" v-if="solution.is_published">
              <el-tag type="success">已发布</el-tag>
            </span>
          </div>
          <div class="article-tags" v-if="solution.tags">
            <el-tag v-for="tag in solution.tags.split(',')" :key="tag" size="small" effect="plain">{{ tag.trim() }}</el-tag>
          </div>
        </header>

        <!-- 解决方案封面 -->
        <div class="article-cover" v-if="solution.cover_image">
          <img :src="solution.cover_image" :alt="solution.title" loading="lazy" @error="$event.target.src='https://via.placeholder.com/800x400?text=Solution'" />
        </div>

        <!-- 解决方案摘要 -->
        <div class="article-summary">
          <h3>方案概述</h3>
          <p>{{ solution.summary }}</p>
        </div>

        <!-- 解决方案内容 -->
        <div class="article-content">
          <h3>方案详情</h3>
          <div class="markdown-body" v-html="renderMd(solution.content)"></div>
        </div>

        <!-- 解决方案标签 -->
        <div class="article-tags" v-if="solution.tags">
          <el-tag
            v-for="tag in solution.tags.split(',')"
            :key="tag"
            size="default"
            effect="light"
          >
            {{ tag.trim() }}
          </el-tag>
        </div>

        <!-- 方案优势 -->
        <div class="advantages-section" v-if="solution.advantages">
          <h3>方案优势</h3>
          <div class="advantages-grid">
            <div
              v-for="(advantage, index) in solution.advantages"
              :key="index"
              class="advantage-item"
            >
              <el-icon class="advantage-icon"><Check /></el-icon>
              <div class="advantage-content">
                <h4>{{ advantage.title }}</h4>
                <p>{{ advantage.description }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- 实施步骤 -->
        <div class="steps-section" v-if="solution.steps">
          <h3>实施步骤</h3>
          <el-timeline>
            <el-timeline-item
              v-for="(step, index) in solution.steps"
              :key="index"
              :color="getStepColor(index)"
            >
              <template #dot>
                <span class="step-number">{{ index + 1 }}</span>
              </template>
              <h4>{{ step.title }}</h4>
              <p>{{ step.description }}</p>
            </el-timeline-item>
          </el-timeline>
        </div>

        <!-- 技术架构 -->
        <div class="architecture-section" v-if="solution.architecture">
          <h3>技术架构</h3>
          <div class="architecture-diagram">
            <img :src="solution.architecture" alt="技术架构图" loading="lazy" @error="$event.target.style.display='none'" />
          </div>
        </div>

        <!-- 成功案例 -->
        <div class="case-studies-section" v-if="solution.case_studies">
          <h3>成功案例</h3>
          <div class="case-studies-grid">
            <div
              v-for="(caseStudy, index) in solution.case_studies"
              :key="index"
              class="case-study-item"
            >
              <div class="case-study-image" v-if="caseStudy.image">
                <img :src="caseStudy.image" :alt="caseStudy.title" loading="lazy" @error="$event.target.style.display='none'" />
              </div>
              <div class="case-study-content">
                <h4>{{ caseStudy.title }}</h4>
                <p>{{ caseStudy.description }}</p>
                <div class="case-study-results">
                  <div
                    v-for="(result, resultIndex) in caseStudy.results"
                    :key="resultIndex"
                    class="case-study-result"
                  >
                    <span class="result-label">{{ result.label }}</span>
                    <span class="result-value">{{ result.value }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 相关解决方案 -->
        <div class="related-solutions" v-if="relatedSolutions.length > 0">
          <h3>相关解决方案</h3>
          <div class="related-list">
            <div
              v-for="item in relatedSolutions"
              :key="item.id"
              class="related-item"
              @click="goToDetail(item.id)"
            >
              <div class="related-content">
                <h4>{{ item.title }}</h4>
                <p>{{ item.summary }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- 联系我们 -->
        <div class="contact-section">
          <h3>联系我们</h3>
          <p class="contact-description">如果您对该解决方案感兴趣，或有任何疑问，请联系我们的解决方案团队。</p>
          <div class="contact-methods">
            <el-button type="primary" size="large">
              <el-icon><Message /></el-icon>
              在线咨询
            </el-button>
            <el-button size="large">
              <el-icon><Phone /></el-icon>
              电话咨询
            </el-button>
            <el-button size="large">
              <el-icon><Document /></el-icon>
              下载方案
            </el-button>
          </div>
        </div>
      </article>

      <!-- 加载失败 -->
      <div v-if="!loading && !solution" class="error-state">
        <el-empty description="解决方案不存在" />
        <el-button type="primary" @click="goBack">返回解决方案列表</el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ArrowLeft, Check, Message, Phone, Document } from '@element-plus/icons-vue'
import { getSolutionById, listSolutions } from '@/api/solutions'
import { useMarkdown } from '@/composables/useMarkdown'
import { useReadingProgress } from '@/composables/useReadingProgress'

const { renderMd } = useMarkdown()
const { progress } = useReadingProgress()

const router = useRouter()
const route = useRoute()
const loading = ref(false)
const solution = ref(null)
const relatedSolutions = ref([])

const formatDate = (d) => d ? new Date(d).toLocaleString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false }).replace(/\//g, '-') : ''

// 获取解决方案详情
const fetchSolutionDetail = async (id) => {
  if (!id) return
  loading.value = true
  try {
    const res = await getSolutionById(id)
    solution.value = res.data || res
    
    await fetchRelatedSolutions()
  } catch (error) {
    solution.value = null
    console.error('获取解决方案详情失败:', error)
  } finally {
    loading.value = false
  }
}

// 获取相关解决方案
const fetchRelatedSolutions = async () => {
  try {
    const res = await listSolutions()
    const data = res?.items || res || []
    const allSolutions = Array.isArray(data) ? data : []
    
    relatedSolutions.value = allSolutions.filter(item => 
      item.id != route.params.id && item.category === solution.value?.category
    ).slice(0, 3)
  } catch (error) {
    console.error('获取相关解决方案失败:', error)
  }
}

// 返回列表页
const goBack = () => {
  router.push('/solutions')
}

// 跳转到解决方案详情
const goToDetail = (id) => {
  router.push(`/solutions/${id}`)
}

// 获取分类标签类型
const getCategoryType = (category) => {
  const categoryMap = {
    '金融服务': 'primary',
    '医疗健康': 'success',
    '制造业': 'warning',
    '零售电商': 'danger',
    '教育科技': 'info',
    '能源环保': '',
    '交通物流': 'info',
    '智能城市': 'info'
  }
  return categoryMap[category] || 'info'
}

// 获取步骤颜色
const getStepColor = (index) => {
  const colors = ['blue', 'green', 'yellow', 'orange', 'purple', 'red']
  return colors[index % colors.length]
}

watch(() => route.params.id, (newId) => {
  if (newId) {
    fetchSolutionDetail(newId)
  }
}, { immediate: true })
</script>

<style scoped>
.reading-progress {
  position: fixed;
  top: 56px;
  left: 0;
  height: 3px;
  background: var(--cyber-neon, #00d4aa);
  box-shadow: 0 0 8px var(--cyber-neon, #00d4aa);
  z-index: 99;
  transition: width 0.1s linear;
}
.solutions-detail-view {
  min-height: 100vh;
  background: var(--app-bg);
  padding: 40px 0;
}

.container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 0 20px;
}

.back-link {
  margin-bottom: 30px;
}

.back-link .el-button {
  color: var(--app-accent);
  font-weight: 500;
}

.solution-article {
  background: var(--app-bg-card);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: var(--el-box-shadow);
  padding: 40px;
}

.article-header {
  text-align: center;
  margin-bottom: 40px;
  padding-bottom: 20px;
  border-bottom: 1px solid var(--app-border);
}

.article-header .el-tag {
  margin-bottom: 16px;
  font-size: 0.875rem;
}

.article-title {
  font-size: 2.5rem;
  color: var(--app-text);
  margin-bottom: 20px;
  font-weight: 700;
  line-height: 1.3;
}

.article-author {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin: 12px 0;
}

.author-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.author-name {
  font-weight: 500;
  color: var(--app-text);
}
.author-link { text-decoration: none; color: inherit; }
.author-link:hover .author-name { color: var(--cyber-neon, #00d4aa); }

.article-meta {
  color: var(--app-text-secondary);
  font-size: 0.875rem;
  display: flex;
  gap: 16px;
  justify-content: center;
}

.article-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
  justify-content: center;
}

.article-cover {
  margin: 30px 0;
  border-radius: 8px;
  overflow: hidden;
}

.article-cover img {
  width: 100%;
  height: auto;
  display: block;
}

.article-summary {
  margin-bottom: 40px;
  padding: 20px;
  background: var(--app-bg-secondary);
  border-radius: 8px;
}

.article-summary h3 {
  color: var(--app-text);
  margin-bottom: 16px;
  font-weight: 600;
}

.article-summary p {
  color: var(--app-text-secondary);
  line-height: 1.6;
  font-size: 1.125rem;
}

.article-content {
  margin-bottom: 40px;
}

.article-content h3 {
  color: var(--app-text);
  margin-bottom: 16px;
  font-weight: 600;
}

.article-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 40px;
  padding: 20px;
  background: var(--app-bg-secondary);
  border-radius: 8px;
}

.advantages-section,
.steps-section,
.architecture-section,
.case-studies-section,
.related-solutions,
.contact-section {
  margin-bottom: 40px;
}

.advantages-section h3,
.steps-section h3,
.architecture-section h3,
.case-studies-section h3,
.related-solutions h3,
.contact-section h3 {
  color: var(--app-text);
  margin-bottom: 24px;
  font-weight: 600;
  font-size: 1.5rem;
}

.advantages-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
}

.advantage-item {
  display: flex;
  gap: 16px;
  padding: 20px;
  background: var(--app-bg-secondary);
  border-radius: 8px;
  transition: all 0.3s ease;
}

.advantage-item:hover {
  transform: translateY(-2px);
}

.advantage-icon {
  color: var(--app-accent);
  font-size: 1.5rem;
  flex-shrink: 0;
}

.advantage-content h4 {
  color: var(--app-text);
  margin-bottom: 8px;
  font-weight: 600;
}

.advantage-content p {
  color: var(--app-text-secondary);
  font-size: 0.875rem;
  line-height: 1.5;
}

.steps-section .el-timeline {
  margin-left: 20px;
}

.step-number {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: var(--app-accent);
  color: #fff;
  font-size: 12px;
  font-weight: 600;
}

.steps-section .el-timeline-item {
  margin-bottom: 30px;
}

.steps-section .el-timeline-item h4 {
  color: var(--app-text);
  margin-bottom: 8px;
  font-weight: 600;
}

.steps-section .el-timeline-item p {
  color: var(--app-text-secondary);
  font-size: 0.875rem;
  line-height: 1.5;
}

.architecture-diagram {
  text-align: center;
  margin-bottom: 20px;
}

.architecture-diagram img {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
  box-shadow: var(--el-box-shadow);
}

.case-studies-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.case-study-item {
  padding: 20px;
  background: var(--app-bg-secondary);
  border-radius: 8px;
  transition: all 0.3s ease;
}

.case-study-image {
  margin-bottom: 16px;
  border-radius: 8px;
  overflow: hidden;
}

.case-study-image img {
  width: 100%;
  height: 150px;
  object-fit: cover;
}

.case-study-content h4 {
  color: var(--app-text);
  margin-bottom: 8px;
  font-weight: 600;
}

.case-study-content p {
  color: var(--app-text-secondary);
  font-size: 0.875rem;
  line-height: 1.5;
  margin-bottom: 16px;
}

.case-study-results {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.case-study-result {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 12px;
  background: var(--app-bg);
  border-radius: 6px;
  min-width: 120px;
}

.result-label {
  font-size: 0.75rem;
  color: var(--app-text-secondary);
  font-weight: 500;
}

.result-value {
  font-size: 1rem;
  color: var(--app-text);
  font-weight: 600;
}

.related-list {
  display: grid;
  gap: 20px;
}

.related-item {
  padding: 20px;
  background: var(--app-bg-secondary);
  border-radius: 8px;
  transition: all 0.3s ease;
  cursor: pointer;
}

.related-item:hover {
  transform: translateY(-2px);
}

.related-item h4 {
  color: var(--app-text);
  margin-bottom: 8px;
  font-weight: 600;
}

.related-item p {
  color: var(--app-text-secondary);
  font-size: 0.875rem;
  line-height: 1.5;
}

.contact-section {
  text-align: center;
  padding: 40px;
  background: var(--app-bg-secondary);
  border-radius: 8px;
}

.contact-description {
  color: var(--app-text-secondary);
  margin-bottom: 30px;
  line-height: 1.6;
  font-size: 1.125rem;
}

.contact-methods {
  display: flex;
  justify-content: center;
  gap: 20px;
  flex-wrap: wrap;
}

@media (max-width: 768px) {
  .solution-article {
    padding: 20px;
  }

  .article-title {
    font-size: 1.75rem;
  }

  .advantages-grid,
  .case-studies-grid {
    grid-template-columns: 1fr;
  }

  .contact-methods {
    flex-direction: column;
  }
}
</style>
