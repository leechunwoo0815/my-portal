<template>
  <el-dialog
    v-if="visible"
    :model-value="visible"
    @update:model-value="$emit('update:visible', $event)"
    :width="560"
    class="follow-dialog"
    :close-on-click-modal="true"
  >
    <template #header>
      <div class="fd-tabs">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          :class="['fd-tab', { active: activeTab === tab.key }]"
          @click="switchTab(tab.key)"
        >
          {{ tab.label }}
          <span v-if="tab.count !== undefined" class="fd-tab-count">{{ tab.count }}</span>
        </button>
      </div>
    </template>

    <div v-if="loading" class="fd-loading">
      <el-icon class="is-loading"><Loading /></el-icon> 加载中...
    </div>

    <div v-else-if="items.length === 0" class="fd-empty">
      {{ emptyText }}
    </div>

    <div v-else class="fd-list">
      <div v-for="item in items" :key="item.user_id" class="fd-item">
        <div class="fd-item-left" @click="goToUser(item.user_id)">
          <el-avatar :size="40" :src="item.avatar_url" class="fd-avatar">
            {{ (item.nickname || item.username || '?')[0] }}
          </el-avatar>
        </div>
        <div class="fd-item-info">
          <div class="fd-name-row">
            <span class="fd-name" @click="goToUser(item.user_id)">{{ item.nickname || item.username }}</span>
            <span class="fd-level" :class="'fd-level-' + Math.min(item.level || 1, 10)">
              {{ (item.level || 1) === 999 ? '管理员' : 'LV' + (item.level || 1) }}
            </span>
            <template v-if="isOwner">
              <span v-if="getRelation(item) === 'friend'" class="fd-relation fd-relation-friend">好友</span>
              <span v-else-if="getRelation(item) === 'following'" class="fd-relation fd-relation-following">已关注</span>
              <span v-else-if="getRelation(item) === 'follows_you'" class="fd-relation fd-relation-follows-you">关注你</span>
            </template>
          </div>
          <span class="fd-time">{{ formatTime(item.created_at) }}</span>
        </div>
        <div v-if="isOwner" class="fd-item-actions">
          <el-button
            v-if="activeTab === 'followers' && !isSelf(item.user_id)"
            size="small"
            @click="handleRemoveFollower(item)"
            :loading="actionLoadingMap[item.user_id]"
          >
            移除
          </el-button>
          <el-button
            v-if="!isSelf(item.user_id)"
            size="small"
            :type="isFollowing(item.user_id) ? 'default' : 'primary'"
            @click="handleToggleFollow(item)"
            :loading="actionLoadingMap[item.user_id]"
          >
            {{ isFollowing(item.user_id) ? '取消关注' : '关注' }}
          </el-button>
          <el-button
            v-if="!isSelf(item.user_id)"
            size="small"
            @click="sendMessage(item.user_id)"
          >
            私信
          </el-button>
        </div>
        <div v-else-if="!isSelf(item.user_id)" class="fd-item-actions">
          <el-button
            size="small"
            :type="isFollowing(item.user_id) ? 'default' : 'primary'"
            @click="handleToggleFollow(item)"
            :loading="actionLoadingMap[item.user_id]"
          >
            {{ isFollowing(item.user_id) ? '取消关注' : '关注' }}
          </el-button>
          <el-button
            size="small"
            @click="sendMessage(item.user_id)"
          >
            私信
          </el-button>
        </div>
      </div>
    </div>

    <div v-if="total > pageSize" class="fd-pagination">
      <el-pagination
        small
        layout="prev, pager, next"
        :total="total"
        :page-size="pageSize"
        :current-page="currentPage"
        @current-change="handlePageChange"
      />
    </div>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { Loading } from '@element-plus/icons-vue'
import { socialApi } from '@/api/social'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

const props = defineProps<{
  visible: boolean
  userId: number
  defaultTab?: 'following' | 'followers' | 'friends'
  followingCount?: number
  followersCount?: number
  friendsCount?: number
}>()

const emit = defineEmits<{
  'update:visible': [value: boolean]
  'follow-changed': []
}>()

const router = useRouter()
const authStore = useAuthStore()
const activeTab = ref<'following' | 'followers' | 'friends'>(
  props.defaultTab === 'friends' && authStore.user?.id !== props.userId ? 'following' : (props.defaultTab || 'following')
)
const items = ref<any[]>([])
const loading = ref(false)
const total = ref(0)
const currentPage = ref(1)
const pageSize = 20
const actionLoadingMap = ref<Record<number, boolean>>({})
const myFollowingIds = ref<Set<number>>(new Set())

const tabs = computed(() => {
  const list = [
    { key: 'following' as const, label: '关注', count: props.followingCount },
    { key: 'followers' as const, label: '粉丝', count: props.followersCount },
  ]
  if (isOwner.value) {
    list.push({ key: 'friends' as const, label: '好友', count: props.friendsCount })
  }
  return list
})

const emptyText = computed(() => {
  if (activeTab.value === 'following') return '还没有关注任何人'
  if (activeTab.value === 'followers') return '还没有粉丝'
  return '还没有互相关注的好友'
})

const isOwner = computed(() => authStore.user?.id === props.userId)

const isSelf = (userId: number) => authStore.user?.id === userId

const isFollowing = (userId: number) => myFollowingIds.value.has(userId)

const getRelation = (item: any) => {
  // is_following_me is relative to profile owner (from backend)
  const ownerFollowsBack = item.is_following_me
  if (activeTab.value === 'following') {
    // Following tab: owner follows them. is_following_me = they follow owner back
    if (ownerFollowsBack) return 'friend'
    return 'following'
  }
  if (activeTab.value === 'followers') {
    // Followers tab: they follow owner. is_following_me = owner follows them back
    if (ownerFollowsBack) return 'friend'
    return 'follows_you'
  }
  // Friends tab: always mutual
  return 'friend'
}

const formatTime = (t?: string) => {
  if (!t) return ''
  const diff = Date.now() - new Date(t).getTime()
  const m = Math.floor(diff / 60000)
  if (m < 1) return '刚刚'
  if (m < 60) return `${m}分钟前`
  const h = Math.floor(m / 60)
  if (h < 24) return `${h}小时前`
  const d = Math.floor(h / 24)
  if (d < 30) return `${d}天前`
  return new Date(t).toLocaleDateString('zh-CN')
}

const switchTab = (tab: 'following' | 'followers' | 'friends') => {
  activeTab.value = tab
  currentPage.value = 1
  loadList()
}

const loadList = async () => {
  loading.value = true
  items.value = []
  total.value = 0
  try {
    let res: any
    if (activeTab.value === 'following') {
      res = await socialApi.getFollowing(props.userId, currentPage.value, pageSize)
    } else if (activeTab.value === 'followers') {
      res = await socialApi.getFollowers(props.userId, currentPage.value, pageSize)
    } else {
      res = await socialApi.getFriends(props.userId, currentPage.value, pageSize)
    }
    items.value = res?.items || []
    total.value = res?.total || 0

    if (isOwner.value) {
      // For the owner, use is_following_me from API to build following set
      // Following tab: all items are people owner follows; is_following_me = they follow back
      // Followers tab: is_following_me = owner follows them back
      // Friends tab: all mutual
      if (activeTab.value === 'following') {
        myFollowingIds.value = new Set(items.value.map((i: any) => i.user_id))
      } else {
        // For followers/friends, merge with existing following ids
        const following = new Set(myFollowingIds.value)
        for (const item of items.value) {
          if (item.is_following_me || activeTab.value === 'friends') {
            following.add(item.user_id)
          }
        }
        myFollowingIds.value = following
      }
    } else if (authStore.isLoggedIn) {
      // For non-owners, fetch viewer's following list for follow/unfollow button
      try {
        const myRes: any = await socialApi.getFollowing(authStore.user!.id, 1, 100)
        myFollowingIds.value = new Set((myRes?.items || []).map((i: any) => i.user_id))
      } catch {
        // Non-critical
      }
    }
  } catch (e) {
    console.error('FollowDialog loadList error:', e)
    items.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

const handleToggleFollow = async (item: any) => {
  actionLoadingMap.value[item.user_id] = true
  try {
    const res: any = await socialApi.toggleFollow(item.user_id)
    if (res.is_following) {
      myFollowingIds.value.add(item.user_id)
    } else {
      myFollowingIds.value.delete(item.user_id)
    }
    emit('follow-changed')
  } catch {
    ElMessage.error('操作失败')
  } finally {
    actionLoadingMap.value[item.user_id] = false
  }
}

const handleRemoveFollower = async (item: any) => {
  actionLoadingMap.value[item.user_id] = true
  try {
    await socialApi.removeFollower(item.user_id)
    items.value = items.value.filter(i => i.user_id !== item.user_id)
    total.value--
    emit('follow-changed')
    ElMessage.success('已移除该粉丝')
  } catch {
    ElMessage.error('操作失败')
  } finally {
    actionLoadingMap.value[item.user_id] = false
  }
}

const sendMessage = (userId: number) => {
  emit('update:visible', false)
  router.push(`/messages?userId=${userId}`)
}

const goToUser = (userId: number) => {
  emit('update:visible', false)
  router.push(`/user/${userId}`)
}

const handlePageChange = (page: number) => {
  currentPage.value = page
  loadList()
}

// Load data when dialog becomes visible
onMounted(() => {
  if (props.visible) {
    nextTick(() => loadList())
  }
})

watch(() => props.visible, (val) => {
  if (val) {
    const tab = props.defaultTab || 'following'
    activeTab.value = tab === 'friends' && !isOwner.value ? 'following' : tab
    currentPage.value = 1
    nextTick(() => loadList())
  }
})

watch(() => props.defaultTab, (tab) => {
  if (tab && props.visible) {
    const actualTab = tab === 'friends' && !isOwner.value ? 'following' : tab
    switchTab(actualTab)
  }
})
</script>

<style scoped>
.fd-tabs {
  display: flex;
  gap: 4px;
  background: var(--app-bg, #f5f7fa);
  border-radius: 8px;
  padding: 3px;
}

.fd-tab {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  background: transparent;
  color: var(--app-text-secondary, #909399);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  font-family: inherit;
}

.fd-tab.active {
  background: var(--app-accent, #409eff);
  color: #fff;
}

.fd-tab:not(.active):hover {
  color: var(--app-text, #303133);
  background: var(--app-bg-secondary, #f0f0f0);
}

.fd-tab-count {
  font-size: 12px;
  opacity: 0.8;
}

.fd-loading, .fd-empty {
  text-align: center;
  padding: 40px 0;
  color: var(--app-text-secondary, #909399);
  font-size: 14px;
}

.fd-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 400px;
  overflow-y: auto;
}

.fd-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  border-radius: 8px;
  background: var(--app-bg-card, #fff);
  border: 1px solid var(--app-border, #e4e7ed);
  transition: border-color 0.2s;
}

.fd-item:hover {
  border-color: var(--app-accent, #409eff);
}

.fd-item-left {
  cursor: pointer;
  flex-shrink: 0;
}

.fd-avatar {
  transition: opacity 0.2s;
}

.fd-item-left:hover .fd-avatar {
  opacity: 0.8;
}

.fd-item-info {
  flex: 1;
  min-width: 0;
}

.fd-name-row {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.fd-name {
  font-weight: 600;
  font-size: 14px;
  color: var(--app-text, #303133);
  cursor: pointer;
}

.fd-name:hover {
  color: var(--app-accent, #409eff);
}

.fd-level {
  font-size: 10px;
  padding: 1px 6px;
  border-radius: 6px;
  color: #fff;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.fd-level-1, .fd-level-2 { background: #909399; }
.fd-level-3, .fd-level-4 { background: #409eff; }
.fd-level-5, .fd-level-6 { background: #67c23a; }
.fd-level-7, .fd-level-8 { background: #e6a23c; }
.fd-level-9, .fd-level-10 { background: #f56c6c; }

.fd-relation {
  font-size: 10px;
  padding: 1px 6px;
  border-radius: 6px;
  font-weight: 500;
}

.fd-relation-friend {
  background: #67c23a;
  color: #fff;
}

.fd-relation-following {
  background: var(--app-accent, #409eff);
  color: #fff;
}

.fd-relation-follows-you {
  background: var(--app-bg-secondary, #f0f0f0);
  color: var(--app-text-secondary, #909399);
  border: 1px solid var(--app-border, #e4e7ed);
}

.fd-time {
  font-size: 12px;
  color: var(--app-text-secondary, #909399);
}

.fd-item-actions {
  display: flex;
  gap: 6px;
  flex-shrink: 0;
}

.fd-pagination {
  display: flex;
  justify-content: center;
  margin-top: 16px;
}
</style>
