<template>
  <div class="profile-page">
    <el-card class="profile-header">
      <div v-if="loading" class="profile-skeleton">
        <div class="skel-avatar" />
        <div class="skel-details">
          <div class="skel-bone skel-name" />
          <div class="skel-bone skel-bio" />
          <div class="skel-stats">
            <div class="skel-bone skel-stat" />
            <div class="skel-bone skel-stat" />
            <div class="skel-bone skel-stat" />
            <div class="skel-bone skel-stat" />
          </div>
          <div class="skel-bone skel-progress" />
        </div>
      </div>
      <div class="user-info" v-else-if="user">
        <div class="avatar-section">
          <el-avatar :size="80" :src="user.avatar_url">
            {{ (user.nickname || user.username)?.charAt(0)?.toUpperCase() }}
          </el-avatar>
          <div class="level-badge font-mono" :class="`level-${Math.min(user.level || 1, 10)}`">
            LV{{ user.level === 999 ? '∞' : (user.level || 1) }}
          </div>
        </div>
        <div class="details">
          <h2>
            {{ user.nickname || user.username }}
            <el-tag :type="levelType" size="small">{{ levelText }}</el-tag>
          </h2>
          <p class="bio">{{ user.bio || '这个人很懒，什么都没写' }}</p>
          <div class="stats">
            <div class="stat-item">
              <span class="stat-value font-mono">{{ blogs.length }}</span>
              <span class="stat-label">文章</span>
            </div>
            <el-divider direction="vertical" />
            <div class="stat-item clickable-stat" @click="openFollowDialog('following')">
              <span class="stat-value font-mono">{{ user.following_count || 0 }}</span>
              <span class="stat-label">关注</span>
            </div>
            <el-divider direction="vertical" />
            <div class="stat-item clickable-stat" @click="openFollowDialog('followers')">
              <span class="stat-value font-mono">{{ user.followers_count || 0 }}</span>
              <span class="stat-label">粉丝</span>
            </div>
            <el-divider direction="vertical" />
            <div class="stat-item clickable-stat" @click="openFollowDialog('friends')">
              <span class="stat-value font-mono">{{ user.friends_count || 0 }}</span>
              <span class="stat-label">好友</span>
            </div>
            <el-divider direction="vertical" />
            <div class="stat-item">
              <span class="stat-value font-mono">{{ user.total_likes || 0 }}</span>
              <span class="stat-label">获赞</span>
            </div>
            <el-divider direction="vertical" />
            <div class="stat-item">
              <span class="stat-value font-mono text-cyber-amber">{{ user.total_points || 0 }}</span>
              <span class="stat-label">积分</span>
            </div>
          </div>
          <div class="level-progress" v-if="(user.level || 1) < 10">
            <div class="progress-label">
              <span>{{ levelText }}</span>
              <span class="font-mono">→</span>
              <span>LV{{ (user.level || 1) + 1 }}</span>
              <span class="progress-detail">还需 {{ pointsNeeded }} 积分</span>
            </div>
            <div class="cyber-progress">
              <div class="cyber-progress-bar" :style="{ width: levelProgress + '%' }" />
            </div>
          </div>
          <div class="actions" v-if="authStore.isLoggedIn && !isMe">
            <el-button
              :type="followStatus.is_following ? 'default' : 'primary'"
              @click="toggleFollow"
              :loading="followLoading"
            >
              {{ followStatus.is_following ? '取消关注' : '关注' }}
            </el-button>
            <el-button @click="goMessage">发私信</el-button>
          </div>
          <div class="actions" v-if="isMe">
            <el-button type="primary" @click="goEditProfile">编辑资料</el-button>
            <CheckinButton />
          </div>
        </div>
      </div>
    </el-card>

    <el-card class="profile-achievements" v-if="isMe && achievements.length">
      <template #header>
        <div class="card-title font-mono">
          <span class="prefix">>_</span> 成就墙
          <span class="ach-count">{{ unlockedCount }}/{{ achievements.length }}</span>
        </div>
      </template>
      <div class="achievements-row">
        <div
          v-for="item in achievements.slice(0, 8)"
          :key="item.code"
          class="ach-badge"
          :class="[`tier-${item.tier}`, { 'locked': !item.is_unlocked }]"
          :title="item.is_unlocked ? item.name : '???'"
        >
          <span class="ach-icon">{{ item.is_unlocked ? item.icon : '🔒' }}</span>
          <span class="ach-name">{{ item.is_unlocked ? item.name : '???' }}</span>
        </div>
        <router-link v-if="achievements.length > 8" to="/admin/profile" class="ach-more">
          查看全部 →
        </router-link>
      </div>
    </el-card>

    <ContributionGraph v-if="checkinDates.length" :dates="checkinDates" class="profile-contribution" />

    <el-card class="profile-tabs">
      <el-tabs v-model="activeTab">
        <el-tab-pane label="文章" name="blogs">
          <el-empty v-if="blogs.length === 0" description="暂无文章">
            <el-button v-if="isMe" type="primary" size="small" @click="$router.push('/admin/blogs')">写文章</el-button>
          </el-empty>
          <div v-for="blog in blogs" :key="blog.id" class="list-item">
            <router-link :to="`/blog/${blog.id}`">{{ blog.title }}</router-link>
            <span class="date">{{ new Date(blog.created_at).toLocaleDateString() }}</span>
          </div>
        </el-tab-pane>
        <el-tab-pane label="项目" name="projects">
          <el-empty v-if="projects.length === 0" description="暂无项目">
            <el-button v-if="isMe" type="primary" size="small" @click="$router.push('/admin/portfolio')">创建项目</el-button>
          </el-empty>
          <div v-for="proj in projects" :key="proj.id" class="list-item">
            <router-link :to="`/portfolio/${proj.id}`">{{ proj.title }}</router-link>
            <span class="date">{{ new Date(proj.created_at).toLocaleDateString() }}</span>
          </div>
        </el-tab-pane>
        <el-tab-pane label="动态" name="moments">
          <div v-if="isMe" class="moment-post-box">
            <el-input
              v-model="momentContent"
              type="textarea"
              :rows="3"
              placeholder="分享你的想法..."
              maxlength="1000"
              show-word-limit
            />
            <div v-if="momentImages.length" class="moment-upload-preview">
              <div v-for="(img, idx) in momentImages" :key="idx" class="preview-item">
                <el-image :src="img" fit="cover" style="width:80px;height:80px;border-radius:4px" />
                <el-icon class="remove-btn" @click="momentImages.splice(idx, 1)"><CircleClose /></el-icon>
              </div>
            </div>
            <div class="moment-post-actions">
              <el-popover trigger="click" :width="320">
                <template #reference>
                  <el-button size="small">😊</el-button>
                </template>
                <div class="emoji-grid">
                  <span v-for="e in emojiList" :key="e" class="emoji-item" @click="momentContent += e">{{ e }}</span>
                </div>
              </el-popover>
              <el-upload
                :action="uploadUrl"
                :headers="uploadHeaders"
                :data="{ module: 'moment' }"
                :show-file-list="false"
                :before-upload="beforeImageUpload"
                :on-success="onImageUploaded"
                accept="image/*"
              >
                <el-button size="small">📷 图片</el-button>
              </el-upload>
              <el-button type="primary" size="small" :loading="postingMoment" :disabled="!momentContent.trim() && momentImages.length === 0" @click="postMoment">发布动态</el-button>
            </div>
          </div>
          <el-empty v-if="moments.length === 0" description="暂无动态">
            <el-button v-if="isMe" type="primary" size="small" @click="activeTab = 'moments'">发布动态</el-button>
          </el-empty>
          <div v-for="m in moments" :key="m.id" class="moment-item">
            <div class="moment-header">
              <el-avatar :size="32" :src="m.author?.avatar_url">{{ m.author?.username?.charAt(0) }}</el-avatar>
              <span class="moment-author">{{ m.author?.nickname || m.author?.username }}</span>
              <span class="date">{{ new Date(m.created_at).toLocaleDateString() }}</span>
            </div>
            <p class="moment-content">{{ m.content }}</p>
            <div v-if="m.images && m.images.length" class="moment-images-grid" :class="`grid-${Math.min(m.images.length, 9)}`">
              <el-image v-for="(img, idx) in m.images.slice(0, 9)" :key="idx" :src="img" fit="cover" :preview-src-list="m.images" :initial-index="idx" class="grid-img" />
            </div>
            <div class="moment-stats">
              <span>❤️ {{ m.likes_count || 0 }}</span>
              <span>💬 {{ m.comments_count || 0 }}</span>
              <el-popconfirm
                title="确定删除这条动态？"
                confirm-button-text="确定"
                cancel-button-text="取消"
                @confirm="deleteMoment(m.id)"
              >
                <template #reference>
                  <el-button v-if="isMe" size="small" type="danger" text>删除</el-button>
                </template>
              </el-popconfirm>
            </div>
          </div>
        </el-tab-pane>
        <el-tab-pane label="收藏" name="favorites">
          <el-empty v-if="favorites.length === 0" description="暂无收藏">
            <el-button type="primary" size="small" @click="$router.push('/blog')">去浏览</el-button>
          </el-empty>
          <div v-for="fav in favorites" :key="fav.id" class="list-item">
            <router-link :to="`/blog/${fav.id}`">{{ fav.title }}</router-link>
            <span class="date">{{ new Date(fav.created_at).toLocaleDateString() }}</span>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <FollowDialog
      v-if="user"
      v-model:visible="followDialogVisible"
      :user-id="userId"
      :default-tab="followDialogTab"
      :following-count="user.following_count || 0"
      :followers-count="user.followers_count || 0"
      :friends-count="user.friends_count || 0"
      @follow-changed="onFollowChanged"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { CircleClose } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { userApi } from '@/api/user'
import { socialApi } from '@/api/social'
import { momentApi } from '@/api/moment'
import { achievementApi, checkinApi } from '@/api/achievement'
import CheckinButton from '@/components/checkin/CheckinButton.vue'
import ContributionGraph from '@/components/ContributionGraph.vue'
import FollowDialog from '@/components/FollowDialog.vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const userId = computed(() => parseInt(route.params.id as string))
const isMe = computed(() => authStore.user && userId.value === authStore.user.id)
const activeTab = ref('blogs')
const loading = ref(false)
const followLoading = ref(false)
const postingMoment = ref(false)
const momentContent = ref('')
const momentImages = ref<string[]>([])
const user = ref<any>(null)
const followStatus = reactive({ is_following: false, is_followed_by: false, is_mutual: false })
const blogs = ref<any[]>([])
const checkinDates = ref<string[]>([])
const projects = ref<any[]>([])
const moments = ref<any[]>([])
const favorites = ref<any[]>([])
const achievements = ref<any[]>([])
const unlockedCount = ref(0)
const followDialogVisible = ref(false)
const followDialogTab = ref<'following' | 'followers' | 'friends'>('following')

const uploadUrl = '/api/v1/upload/image'
const uploadHeaders = computed(() => ({
  Authorization: `Bearer ${authStore.token}`
}))

const emojiList = ['😀','😂','🤣','😊','😍','🥰','😎','🤩','😘','😗','😋','😛','😜','🤪','😝','🤑','🤗','🤭','🤫','🤔','🤐','🤨','😐','😑','😶','😏','😒','🙄','😬','🤥','😌','😔','😪','🤤','😴','😷','🤒','🤕','🤢','🤮','❤️','🧡','💛','💚','💙','💜','🖤','🤍','💔','❣️','💕','💞','💓','💗','💖','💘','💝','🔥','⭐','🌟','✨','💯','🎉','🎊','👍','👎','👏','🙌','🤝','🙏']

const beforeImageUpload = (file: File) => {
  const isImage = file.type.startsWith('image/')
  const isLt10M = file.size / 1024 / 1024 < 10
  if (!isImage) ElMessage.error('只能上传图片')
  if (!isLt10M) ElMessage.error('图片不能超过 10MB')
  return isImage && isLt10M
}

const onImageUploaded = (response: any) => {
  if (momentImages.value.length >= 9) {
    ElMessage.warning('最多上传 9 张图片')
    return
  }
  momentImages.value.push(response.url)
}

const levelText = computed(() => {
  if (user.value?.level === 999) return '管理员'
  return `LV${user.value?.level || 1}`
})

const levelType = computed(() => {
  if (user.value?.level === 999) return 'success'
  if (user.value?.level >= 8) return 'warning'
  if (user.value?.level >= 6) return 'info'
  if (user.value?.level >= 4) return 'primary'
  return 'info'
})

const levelThresholds = [0, 100, 300, 900, 1500, 3000, 5000, 10000, 20000, 50000]

const levelProgress = computed(() => {
  const lv = user.value?.level || 1
  if (lv >= 10) return 100
  const cur = levelThresholds[lv - 1] || 0
  const next = levelThresholds[lv] || 0
  if (next <= cur) return 100
  return Math.min(100, Math.floor((((user.value?.total_points || 0) - cur) / (next - cur)) * 100))
})

const pointsNeeded = computed(() => {
  const lv = user.value?.level || 1
  if (lv >= 10) return 0
  const next = levelThresholds[lv] || 0
  return Math.max(0, next - (user.value?.total_points || 0))
})

const fetchUserBlogs = async () => {
  try {
    const res: any = await userApi.getUserBlogs(userId.value)
    blogs.value = res.items || res || []
  } catch {
    blogs.value = []
  }
}

const loadCheckinCalendar = async () => {
  try {
    const allDates: string[] = []
    const now = new Date()
    for (let i = 0; i < 12; i++) {
      const d = new Date(now.getFullYear(), now.getMonth() - i, 1)
      const res: any = await checkinApi.getCalendar(d.getFullYear(), d.getMonth() + 1)
      const days = res?.days || res?.dates || res || []
      if (Array.isArray(days)) {
        for (const day of days) {
          if (typeof day === 'string') allDates.push(day)
          else if (day?.date) allDates.push(day.date)
        }
      }
    }
    checkinDates.value = allDates
  } catch {}
}

const loadAchievements = async () => {
  if (!isMe.value) return
  try {
    const res: any = await achievementApi.getMy()
    achievements.value = res.items || []
    unlockedCount.value = res.unlocked_count || achievements.value.filter((a: any) => a.is_unlocked).length
  } catch {}
}

const loadProfile = async () => {
  user.value = null
  blogs.value = []
  projects.value = []
  moments.value = []
  favorites.value = []
  achievements.value = []
  loading.value = true
  try {
    user.value = await userApi.getUserProfile(userId.value)
    if (authStore.isLoggedIn) {
      const status: any = await socialApi.getFollowStatus(userId.value)
      Object.assign(followStatus, status)
    }
    const [projRes, momRes]: any[] = await Promise.all([
      userApi.getUserProjects(userId.value),
      userApi.getUserMoments(userId.value),
    ])
    await fetchUserBlogs()
    projects.value = projRes.items || []
    moments.value = momRes.items || []
  } catch (err: any) {
    ElMessage.error('加载用户信息失败')
  } finally {
    loading.value = false
  }
  loadAchievements()
  loadCheckinCalendar()
}

const toggleFollow = async () => {
  followLoading.value = true
  try {
    const res: any = await socialApi.toggleFollow(userId.value)
    followStatus.is_following = res.is_following
  } catch (err: any) {
    ElMessage.error('操作失败')
  } finally {
    followLoading.value = false
  }
}

const goMessage = () => {
  router.push({ path: '/messages', query: { userId: String(userId.value) } })
}

const goEditProfile = () => {
  router.push('/admin/profile')
}

const openFollowDialog = (tab: 'following' | 'followers' | 'friends') => {
  followDialogTab.value = tab
  followDialogVisible.value = true
}

const onFollowChanged = async () => {
  try {
    const status: any = await socialApi.getFollowStatus(userId.value)
    Object.assign(followStatus, status)
    user.value.following_count = status.following_count
    user.value.followers_count = status.followers_count
    // Refresh friends count from friends API
    const friendsRes: any = await socialApi.getFriends(userId.value, 1, 1)
    user.value.friends_count = friendsRes?.total || 0
  } catch {}
}
const postMoment = async () => {
  if (!momentContent.value.trim() && momentImages.value.length === 0) return
  postingMoment.value = true
  try {
    await momentApi.create({
      content: momentContent.value.trim(),
      images: momentImages.value,
    })
    momentContent.value = ''
    momentImages.value = []
    ElMessage.success('动态发布成功')
    await loadProfile()
  } catch (err: any) {
    ElMessage.error(err?.response?.data?.detail || '发布失败')
  } finally {
    postingMoment.value = false
  }
}

const deleteMoment = async (id: number) => {
  try {
    await momentApi.delete(id)
    ElMessage.success('动态已删除')
    await loadProfile()
  } catch (err: any) {
    ElMessage.error(err?.response?.data?.detail || '删除失败')
  }
}

watch(userId, () => {
  if (userId.value) loadProfile()
})

onMounted(() => {
  if (userId.value) loadProfile()
})
</script>

<style scoped lang="scss">
.profile-page { max-width: 1200px; margin: 0 auto; padding: 20px; }
.profile-header { margin-bottom: 20px; }

.user-info { display: flex; gap: 30px; }
.avatar-section { position: relative; flex-shrink: 0; }
.level-badge {
  position: absolute;
  bottom: -4px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 0.65rem;
  padding: 1px 8px;
  border-radius: 8px;
  color: #fff;
  white-space: nowrap;
}
.level-badge.level-1, .level-badge.level-2, .level-badge.level-3 { background: #909399; }
.level-badge.level-4, .level-badge.level-5 { background: #409eff; }
.level-badge.level-6, .level-badge.level-7 { background: #9b59b6; }
.level-badge.level-8, .level-badge.level-9 { background: #e6a23c; }
.level-badge.level-10 { background: linear-gradient(135deg, #00d4aa, #f0b429); }

.details { flex: 1; }
.details h2 { display: flex; align-items: center; gap: 10px; color: var(--cyber-text, var(--app-text)); }
.bio { color: var(--cyber-muted, var(--app-text-secondary)); margin: 10px 0; }

.stats { display: flex; gap: 20px; margin: 15px 0; align-items: center; }
.stat-item { display: flex; flex-direction: column; align-items: center; }
.stat-value { font-size: 1.2rem; font-weight: 700; color: var(--cyber-text, var(--app-text)); }
.stat-label { font-size: 0.75rem; color: var(--cyber-muted, var(--app-text-secondary)); margin-top: 2px; }
.clickable-stat { cursor: pointer; transition: color 0.2s; }
.clickable-stat:hover .stat-value { color: var(--cyber-neon, var(--app-accent)); }

.level-progress { margin-top: 20px; }
.progress-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--cyber-muted, var(--app-text-secondary));
  margin-bottom: 6px;
}
.progress-detail { font-size: 12px; margin-left: auto; }
.cyber-progress {
  height: 6px;
  background: var(--cyber-border, var(--app-border));
  border-radius: 3px;
  overflow: hidden;
}
.cyber-progress-bar {
  height: 100%;
  background: linear-gradient(90deg, var(--cyber-neon, #00d4aa), var(--cyber-amber, #f0b429));
  border-radius: 3px;
  transition: width 0.5s ease;
}

.actions { margin-top: 20px; display: flex; gap: 8px; align-items: center; }

.profile-achievements { margin-bottom: 20px; }
.profile-contribution { margin-bottom: 20px; }
.card-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--cyber-text, var(--app-text));
}
.card-title .prefix { color: var(--cyber-neon, var(--app-accent)); }
.ach-count {
  font-size: 0.78rem;
  color: var(--cyber-muted, var(--app-text-secondary));
  margin-left: auto;
}
.achievements-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
}
.ach-badge {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 8px 10px;
  border-radius: 8px;
  background: var(--cyber-bg, var(--app-bg));
  border: 1px solid var(--cyber-border, var(--app-border));
  min-width: 70px;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.ach-badge:hover {
  border-color: var(--cyber-neon, var(--app-accent));
  box-shadow: 0 0 8px rgba(0,212,170,0.15);
}
.ach-badge.locked { opacity: 0.5; }
.ach-badge.tier-bronze { border-left: 3px solid #cd7f32; }
.ach-badge.tier-silver { border-left: 3px solid #c0c0c0; }
.ach-badge.tier-gold { border-left: 3px solid #ffd700; }
.ach-badge.tier-diamond { border-left: 3px solid #b9f2ff; box-shadow: 0 0 10px rgba(185,242,255,0.15); }
.ach-icon { font-size: 20px; }
.ach-name { font-size: 0.68rem; color: var(--cyber-muted, var(--app-text-secondary)); text-align: center; white-space: nowrap; }
.ach-more {
  font-size: 0.8rem;
  color: var(--cyber-neon, var(--app-accent));
  text-decoration: none;
  margin-left: 8px;
}
.ach-more:hover { text-decoration: underline; }

.profile-tabs { margin-bottom: 20px; }
.list-item { padding: 10px 0; border-bottom: 1px solid var(--cyber-border, var(--app-border)); display: flex; justify-content: space-between; }
.list-item a { color: var(--cyber-text, var(--app-text)); text-decoration: none; }
.list-item a:hover { color: var(--cyber-neon, var(--app-accent)); }
.moment-item { padding: 12px 0; border-bottom: 1px solid var(--cyber-border, var(--app-border)); }
.moment-header { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.moment-author { font-weight: 500; color: var(--cyber-text, var(--app-text)); }
.moment-content { font-size: 14px; line-height: 1.6; color: var(--cyber-text, var(--app-text)); margin-bottom: 8px; }
.moment-stats { display: flex; gap: 16px; font-size: 13px; color: var(--cyber-muted, var(--app-text-secondary)); }
.moment-post-box { margin-bottom: 16px; padding: 12px; background: var(--cyber-card, var(--app-bg-card)); border-radius: 8px; border: 1px solid var(--cyber-border, var(--app-border)); }
.moment-post-actions { display: flex; gap: 8px; align-items: center; margin-top: 8px; }
.moment-upload-preview { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 8px; }
.preview-item { position: relative; }
.remove-btn { position: absolute; top: -6px; right: -6px; cursor: pointer; color: #f56c6c; font-size: 18px; background: #fff; border-radius: 50%; }
.emoji-grid { display: grid; grid-template-columns: repeat(10, 1fr); gap: 4px; max-height: 200px; overflow-y: auto; }
.emoji-item { cursor: pointer; font-size: 20px; text-align: center; padding: 4px; border-radius: 4px; }
.emoji-item:hover { background: var(--el-fill-color-light); }
.moment-images-grid { display: grid; gap: 4px; border-radius: 6px; overflow: hidden; max-width: 300px; margin-bottom: 8px; }
.moment-images-grid.grid-1 { grid-template-columns: 1fr; }
.moment-images-grid.grid-1 .grid-img { width: 200px; height: 200px; }
.moment-images-grid.grid-2 { grid-template-columns: 1fr 1fr; }
.moment-images-grid.grid-2 .grid-img { width: 148px; height: 148px; }
.moment-images-grid.grid-4 { grid-template-columns: 1fr 1fr; }
.moment-images-grid.grid-4 .grid-img { width: 148px; height: 148px; }
.moment-images-grid.grid-3, .moment-images-grid.grid-5, .moment-images-grid.grid-6 { grid-template-columns: 1fr 1fr 1fr; }
.moment-images-grid.grid-3 .grid-img, .moment-images-grid.grid-5 .grid-img, .moment-images-grid.grid-6 .grid-img { width: 97px; height: 97px; }
.moment-images-grid.grid-7, .moment-images-grid.grid-8, .moment-images-grid.grid-9 { grid-template-columns: 1fr 1fr 1fr; }
.moment-images-grid.grid-7 .grid-img, .moment-images-grid.grid-8 .grid-img, .moment-images-grid.grid-9 .grid-img { width: 97px; height: 97px; }
.grid-img { cursor: pointer; }
.date { color: var(--cyber-muted, var(--app-text-secondary)); font-size: 13px; }
.profile-skeleton {
  display: flex;
  gap: 30px;
  animation: skeleton-pulse 1.5s ease-in-out infinite;
}
.skel-avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: var(--cyber-border, var(--app-border));
  flex-shrink: 0;
}
.skel-details {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.skel-bone {
  border-radius: 4px;
  background: var(--cyber-border, var(--app-border));
}
.skel-name { width: 40%; height: 24px; }
.skel-bio { width: 70%; height: 14px; }
.skel-stats {
  display: flex;
  gap: 20px;
  margin-top: 4px;
}
.skel-stat { width: 60px; height: 36px; }
.skel-progress { width: 100%; height: 20px; margin-top: 4px; }
@keyframes skeleton-pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
</style>
